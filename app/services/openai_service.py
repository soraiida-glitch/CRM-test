import json
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.services.text_processing import (
    decode_base64_text,
    extract_email,
    extract_phone_candidates,
    extract_postal_code,
    extract_website,
    normalize_phone_number,
    split_full_name,
)


@dataclass
class ParsedImageLead:
    company: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    fax: str | None = None
    website: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    raw_text: str = ""


@dataclass
class ParsedVoiceLead:
    company: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    description: str | None = None
    raw_text: str = ""


class OpenAIService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.has_openai else None

    @property
    def _supports_responses_api(self) -> bool:
        return self._client is not None and hasattr(self._client, "responses")

    async def judge_inquiry(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self._supports_responses_api:
            return self._judge_inquiry_fallback(payload)

        response = await self._client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You qualify Japanese B2B inquiries for Salesforce lead registration. "
                        "Return JSON with should_register boolean and reason string."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.output_text)
        return {
            "should_register": bool(parsed.get("should_register")),
            "reason": str(parsed.get("reason", "")),
        }

    async def analyze_business_card(self, image_base64: str, mime_type: str) -> ParsedImageLead:
        raw_text = decode_base64_text(image_base64)
        if raw_text:
            return self._parse_text_business_card(raw_text)

        if not self._supports_responses_api:
            return ParsedImageLead(raw_text="")

        response = await self._client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Extract Japanese business card data as JSON only. "
                        "Do not infer missing values. Return null when unknown."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{image_base64}",
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.output_text)
        parsed.setdefault("raw_text", "")
        return ParsedImageLead(**parsed)

    async def transcribe_audio(self, audio_base64: str, filename: str) -> str:
        raw_text = decode_base64_text(audio_base64)
        if raw_text:
            return raw_text
        if self._client is None:
            return ""
        transcription = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, base64.b64decode(audio_base64)),
        )
        return transcription.text

    async def extract_voice_lead(self, raw_text: str) -> ParsedVoiceLead:
        if not self._supports_responses_api:
            return self._parse_voice_text(raw_text)

        response = await self._client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Extract structured lead data from Japanese voice transcription as JSON only. "
                        "Do not infer missing fields."
                    ),
                },
                {"role": "user", "content": raw_text},
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.output_text)
        parsed.setdefault("raw_text", raw_text)
        return ParsedVoiceLead(**parsed)

    async def generate_slide_section(self, kind: str, payload: dict[str, Any]) -> Any:
        return self._generate_slide_section_fallback(kind, payload)

    async def generate_sales_action(
        self, opportunity: dict[str, Any], priority_score: int
    ) -> dict[str, str]:
        if not self._supports_responses_api:
            return {
                "action": f"{opportunity['name']}について今日中に次回接点を設定し、{opportunity['stage']}を前進させる。",
                "action_reason": self._build_sales_action_reason(opportunity, priority_score),
            }

        response = await self._client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a Japanese sales manager. Return JSON with action and action_reason. "
                        "The action must be specific and executable today."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "priority_score": priority_score,
                            "opportunity": opportunity,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.output_text)
        return {
            "action": str(parsed.get("action", "")),
            "action_reason": str(parsed.get("action_reason", "")),
        }

    async def generate_advice(
        self, opportunity: dict[str, Any], similar_cases: list[dict[str, Any]]
    ) -> str:
        if not self._supports_responses_api:
            notes = "\n".join(
                f"- {item['document']}" for item in similar_cases if item.get("document")
            )
            advice = (
                f"{opportunity['name']}は{opportunity['stage']}段階です。"
                "今日中に次回接点を確定し、競合比較への回答を明文化してください。"
            )
            if notes:
                advice = f"{advice}\n\n参考にした過去の成功事例:\n{notes}"
            return advice

        response = await self._client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Provide concise next-action advice in Japanese using the opportunity and winning cases.",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "opportunity": opportunity,
                            "similar_cases": similar_cases,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        )
        return response.output_text

    def _judge_inquiry_fallback(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = payload["inquiry_text"].strip().lower()
        keywords = (
            "implement",
            "pricing",
            "quote",
            "consultation",
            "evaluate",
            "demo",
            "purchase",
            "導入",
            "料金",
            "見積",
            "相談",
            "検討",
            "デモ",
        )
        matched = [word for word in keywords if word in normalized]
        return {
            "should_register": bool(matched),
            "reason": (
                "サービス導入検討や料金問い合わせが含まれており購買意図が明確"
                if matched
                else "購買意図を示す明確な表現が不足"
            ),
        }

    def _parse_text_business_card(self, raw_text: str) -> ParsedImageLead:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        phones = [normalize_phone_number(value) for value in extract_phone_candidates(raw_text)]
        phones = [value for value in phones if value]
        first_name, last_name = split_full_name(lines[2] if len(lines) > 2 else "")
        return ParsedImageLead(
            company=lines[0] if lines else None,
            first_name=first_name,
            last_name=last_name,
            title=lines[1] if len(lines) > 1 else None,
            email=extract_email(raw_text),
            phone=phones[0] if phones else None,
            mobile_phone=phones[1] if len(phones) > 1 else None,
            fax=phones[2] if len(phones) > 2 else None,
            website=extract_website(raw_text),
            street=lines[4] if len(lines) > 4 else None,
            city=None,
            state=None,
            postal_code=extract_postal_code(raw_text),
            country="日本" if raw_text else None,
            raw_text=raw_text,
        )

    def _parse_voice_text(self, raw_text: str) -> ParsedVoiceLead:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        phones = [normalize_phone_number(value) for value in extract_phone_candidates(raw_text)]
        phones = [value for value in phones if value]
        first_name, last_name = split_full_name(lines[2] if len(lines) > 2 else "")
        return ParsedVoiceLead(
            company=lines[0] if lines else None,
            first_name=first_name,
            last_name=last_name,
            title=lines[1] if len(lines) > 1 else None,
            email=extract_email(raw_text),
            phone=phones[0] if phones else None,
            mobile_phone=phones[1] if len(phones) > 1 else None,
            description=lines[-1] if lines else "",
            raw_text=raw_text,
        )

    def _generate_slide_section_fallback(self, kind: str, payload: dict[str, Any]) -> Any:
        if kind == "issues":
            return {
                "issue_1": f"{payload['issues']}ことが商談機会の損失につながっている点。",
                "issue_2": f"{payload['description']}という現行運用が拡張性を阻害している点。",
            }
        if kind == "use_cases":
            return {
                "use_case_1": f"{payload['strategy']}を用いて初動対応を高速化する。",
                "use_case_2": f"{payload['description']}の現場運用に合わせて対応品質を標準化する。",
            }
        if kind == "questions":
            return {
                "needs_and_issues": ["最も時間を要している業務は何ですか。", "改善したいKPIは何ですか。"],
                "data_details": ["元データはどこに保管されていますか。", "再利用できる履歴データはありますか。"],
                "system_infrastructure": ["連携必須の業務システムは何ですか。", "監査や権限制御の要件はありますか。"],
                "organization_structure": ["導入後の運用責任者は誰ですか。", "意思決定に関与する部門はどこですか。"],
                "budget_and_timeline": ["希望導入時期はいつですか。", "予算承認者は誰ですか。"],
            }
        if kind == "insight":
            target_process = (
                "メール返信業務"
                if "email" in payload["name"].lower() or "mail" in payload["strategy"].lower()
                else "営業業務"
            )
            return {
                "target_process": target_process,
                "point_1": "データ形式のばらつきを先に整理する必要があります。",
                "point_2": "既存システムと安全に連携できる認証設計が必要です。",
                "full_sentence": (
                    f"{target_process}は、データ整備とセキュアな連携設計を両立して初めて安定運用できます。"
                ),
            }
        if kind == "case_type":
            source = f"{payload['name']} {payload['strategy']} {payload['description']}".lower()
            if "chat" in source or "pdf" in source:
                return 1
            if "email" in source or "mail" in source or "メール" in source:
                return 2
            if "business card" in source or "name card" in source or "名刺" in source:
                return 3
            return 4
        raise ValueError(f"Unsupported slide section kind: {kind}")

    def _build_sales_action_reason(self, opportunity: dict[str, Any], priority_score: int) -> str:
        reasons = [f"優先度スコア {priority_score}"]
        if not opportunity.get("decision_maker_contacted"):
            reasons.append("決裁者接触が未完了")
        if not opportunity.get("next_step"):
            reasons.append("次アクション未設定")
        return " / ".join(reasons)


def get_openai_service() -> OpenAIService:
    return OpenAIService()
