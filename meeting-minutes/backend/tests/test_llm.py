import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from services.llm import generate_minutes


@pytest.mark.asyncio
async def test_generate_minutes_returns_structured_result():
    """LLM 응답을 파싱하여 구조화된 회의록을 반환해야 한다."""
    mock_llm_response = json.dumps({
        "summary": "테스트 회의 요약",
        "discussions": ["논의사항 1", "논의사항 2"],
        "decisions": ["결정사항 1"],
        "actionItems": ["액션아이템 1"]
    })

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": mock_llm_response}}]
    }

    with patch("services.llm.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await generate_minutes("회의 내용 텍스트")

    assert result["summary"] == "테스트 회의 요약"
    assert len(result["discussions"]) == 2
    assert len(result["decisions"]) == 1
    assert len(result["actionItems"]) == 1


@pytest.mark.asyncio
async def test_generate_minutes_empty_transcript():
    """빈 텍스트가 입력되면 ValueError를 발생시켜야 한다."""
    with pytest.raises(ValueError):
        await generate_minutes("")
