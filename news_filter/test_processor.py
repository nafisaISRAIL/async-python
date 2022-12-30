import pytest
import aiohttp
import pymorphy2

from mock import patch, AsyncMock, MagicMock

from processor import process_article

@pytest.fixture
def morph():
    return pymorphy2.MorphAnalyzer()



@pytest.mark.asyncio
@patch("processor.fetch", new_callable=AsyncMock, return_value="</script></body></html>")
async def test_parse_error(mocked_fetch, morph):
    session = MagicMock()
    result=[]
    await process_article(
        session=session, 
        morph=morph, 
        charged_words=[],
        url="url",
        result=result,
    )
    mocked_fetch.assert_called()
    assert result[0]["status"] == "PARSING_ERROR"


@pytest.mark.asyncio
async def test_fetch_error(morph):
    result=[]
    async with aiohttp.ClientSession() as session:
        await process_article(
            session=session, 
            morph=morph, 
            charged_words=[],
            url="https://lenta/vvvv",
            result=result,
        )
    assert result[0]["status"] == "FETCH_ERROR"
