import json
import os
import time
import urllib.request
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from retriever import retrieve_documents
from prompt import build_prompt
from models import SupportResponse


class SupportState(TypedDict, total=False):
    query: str
    intent: str
    context: str
    answer: str
    sources: list[str]
    confidence: float


def classify_intent(state: SupportState):
    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "track",
        "cancel",
        "cancellation",
        "gift card",
        "support",
        "support hours",
        "order",
        "damaged",
        "missing",
        "fee",
        "pass"
    ]

    if any(keyword in query for keyword in policy_keywords):
        intent = "policy_question"
    else:
        intent = "general_question"

    print(f"Intent: {intent}")

    return {
        "intent": intent
    }


def call_real_llm(prompt: str, max_retries: int = 3) -> str:
    """
    Optional real-LLM path.

    Uses the OpenAI Responses API when MOCK_LLM=0.
    Retries failed API requests up to max_retries times.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required when MOCK_LLM=0."
        )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )

    url = "https://api.openai.com/v1/responses"

    payload = {
        "model": model,
        "input": prompt
    }

    request_data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, max_retries + 1):

        try:

            request = urllib.request.Request(
                url,
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                response_data = json.loads(
                    response.read().decode("utf-8")
                )

            output_text = response_data.get(
                "output_text"
            )

            if output_text:
                return output_text

            raise RuntimeError(
                "LLM response did not contain output_text."
            )

        except Exception as error:

            print(
                f"LLM attempt "
                f"{attempt}/{max_retries} failed: "
                f"{error}"
            )

            if attempt == max_retries:
                raise

            time.sleep(
                2 ** (attempt - 1)
            )

    raise RuntimeError(
        "LLM generation failed."
    )


def generate_validated_llm_response(
    prompt: str,
    max_validation_retries: int = 2
):
    """
    Optional real-LLM generation with Pydantic validation.

    If the LLM output fails validation, retry up to
    2 additional times with a corrective instruction.
    """

    validation_instruction = """
Return ONLY valid JSON with exactly these fields:

{
  "answer": "string",
  "sources": ["string"],
  "confidence": 0.0
}

The confidence value must be between 0.0 and 1.0.
Do not include markdown.
Do not include any extra text.
"""

    current_prompt = (
        prompt
        + "\n\n"
        + validation_instruction
    )

    for attempt in range(
        max_validation_retries + 1
    ):

        raw_output = call_real_llm(
            current_prompt
        )

        try:

            parsed_output = json.loads(
                raw_output
            )

            validated = SupportResponse(
                answer=parsed_output["answer"],
                sources=parsed_output["sources"],
                confidence=parsed_output["confidence"]
            )

            return validated

        except Exception as error:

            print(
                f"Pydantic validation attempt "
                f"{attempt + 1}/"
                f"{max_validation_retries + 1} failed: "
                f"{error}"
            )

            if attempt == max_validation_retries:

                return SupportResponse(
                    answer=(
                        "ERROR: The real-LLM response "
                        "failed Pydantic validation "
                        "after 2 additional retries."
                    ),
                    sources=[],
                    confidence=0.0
                )

            current_prompt = (
                prompt
                + "\n\n"
                + validation_instruction
                + "\n\n"
                + "CORRECTIVE INSTRUCTION: "
                "Your previous response failed "
                "schema validation. "
                "Return ONLY valid JSON matching "
                "the required schema."
            )


def retrieve_and_answer(
    state: SupportState
):
    query = state["query"]

    # Retrieval always runs, including MOCK_LLM mode.
    results = retrieve_documents(
        query,
        top_k=3
    )

    context_parts = []
    sources = []

    for result in results:

        context_parts.append(
            result["document"]
        )

        sources.append(
            f"{result['document_id']}::"
            f"{result['chunk_id']}"
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = build_prompt(
        query,
        context
    )

    mock_llm = os.getenv(
        "MOCK_LLM",
        "1"
    )

    if mock_llm == "1":

        top_chunk = results[0]["document"]

        answer = (
            "Based on the retrieved context: "
            f"{top_chunk[:300]}"
        )

        validated = SupportResponse(
            answer=answer,
            sources=sources,
            confidence=1.0
        )

    else:

        validated = generate_validated_llm_response(
            prompt
        )

    return {
        "context": context,
        "answer": validated.answer,
        "sources": validated.sources,
        "confidence": validated.confidence
    }


def direct_answer(
    state: SupportState
):
    """
    Mock-mode direct answer.

    No retrieval and no LLM call in the
    required MOCK_LLM=1 graded workflow.
    """

    answer = (
        "I can only answer questions about "
        "Zepto policies right now."
    )

    validated = SupportResponse(
        answer=answer,
        sources=[],
        confidence=1.0
    )

    return {
        "answer": validated.answer,
        "sources": validated.sources,
        "confidence": validated.confidence
    }


def route_intent(
    state: SupportState
):
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


workflow = StateGraph(
    SupportState
)

workflow.add_node(
    "classify_intent",
    classify_intent
)

workflow.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

workflow.add_node(
    "direct_answer",
    direct_answer
)

workflow.add_edge(
    START,
    "classify_intent"
)

workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer":
            "retrieve_and_answer",
        "direct_answer":
            "direct_answer"
    }
)

workflow.add_edge(
    "retrieve_and_answer",
    END
)

workflow.add_edge(
    "direct_answer",
    END
)

graph = workflow.compile()


if __name__ == "__main__":

    print(
        "\n--- POLICY QUESTION ---"
    )

    policy_result = graph.invoke(
        {
            "query":
                "How much is the delivery fee "
                "below INR 149?"
        }
    )

    print(
        "Answer:",
        policy_result["answer"]
    )

    print(
        "Sources:",
        policy_result["sources"]
    )

    print(
        "Confidence:",
        policy_result["confidence"]
    )

    print(
        "\n--- GENERAL QUESTION ---"
    )

    general_result = graph.invoke(
        {
            "query":
                "What is artificial intelligence?"
        }
    )

    print(
        "Answer:",
        general_result["answer"]
    )

    print(
        "Sources:",
        general_result["sources"]
    )

    print(
        "Confidence:",
        general_result["confidence"]
    )