from bs4 import BeautifulSoup as bs  

def html_to_text(html: str) -> str:
    """
    Convert HTML to text

    Args:
      html: HTML string
    """
    soup = bs(html, features="html.parser")
    text = soup.get_text()
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split()) # remove extra spaces
    return text
