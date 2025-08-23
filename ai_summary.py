import json
from openai import OpenAI
from typing import Dict, Any, Optional, Tuple
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def get_openai_api_key():
    """Biztonságos API kulcs lekérés Streamlit függőségek nélkül"""
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

class AISummaryGenerator:
    """
    OpenAI API-val történő összefoglaló és javaslat generálás
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializálja az AI Summary Generator-t
        
        Args:
            api_key: OpenAI API kulcs (ha nincs megadva, környezetből veszi)
        """
        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API kulcs szükséges. Állítsd be a OPENAI_API_KEY environment változót.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_summary_and_recommendations(self, json_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generál egy összefoglalót és javaslatokat a JSON adatok alapján
        
        Args:
            json_data: Az elemzés eredményét tartalmazó JSON adatok
            
        Returns:
            Tuple[str, str]: (összefoglaló, javaslatok)
        """
        try:
            # JSON adatok előkészítése
            formatted_data = self._format_json_for_ai(json_data)
            
            # OpenAI API hívás
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Te egy SEO és web optimalizálási szakértő vagy. A feladatod, hogy elemezd a weboldal GEO (Generative Engine Optimization) eredményeit és készíts összefoglalót és javaslatokat."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Készítettem egy generative engine optimization ellenőrzést egy url-ről, az eredményt az alábbi json táblázatban küldöm. ELemezd a teljes JSON fájlt, utána az a feladatod, hogy:

1. Készíts egy összefoglalót a JSON fájlban tárolt eredmények alapján. Légy alapos és szigorú. Haladj végig a HTML adatokon, AI metrikákon, Olvashatóságon, Schema és Google validáláson, SEO tartalmaok, Platformokon és Sebességen is.  (maximum 1000 szó)
2. Készíts egy javaslatot a GEO eredmények javítására az 1. pontban írt összefoglaló alapján. Mindenképp használd fel hozzá a JSON fájlban feltüntetett Javítási javaslatokat is. (maximum 1000 szó, konkrét, végrehajtható lépések)

JSON adatok:
{formatted_data}

Kérlek, válaszolj JSON formátumban az alábbi struktúrával:
{{
    "summary": "Az összefoglaló szövege...",
    "recommendations": "A javaslatok szövege..."
}}"""
                    }
                ],
                temperature=0.7,
                max_tokens=3000  # Csökkentjük a token limitet hogy elférjen a 8192 token kontextusba
            )
            
            # Válasz feldolgozása
            ai_response = response.choices[0].message.content.strip()
            
            try:
                # JSON parsing
                parsed_response = json.loads(ai_response)
                summary = parsed_response.get("summary", "Nem sikerült generálni az összefoglalót.")
                recommendations = parsed_response.get("recommendations", "Nem sikerült generálni a javaslatokat.")
                
                return summary, recommendations
                
            except json.JSONDecodeError:
                # Ha nem valid JSON, próbáljuk szétválasztani manuálisan
                logger.warning("AI válasz nem valid JSON, manuális feldolgozás...")
                return self._parse_ai_response_manually(ai_response)
                
        except Exception as e:
            logger.error(f"Hiba az AI összefoglaló generálása során: {str(e)}")
            error_summary = "Hiba történt az AI összefoglaló generálása során. Kérlek, ellenőrizd az OpenAI API kulcsot és próbáld újra."
            error_recommendations = "Az AI javaslatok nem elérhetők. Manuálisan ellenőrizd az eredményeket és készíts optimalizálási tervet."
            return error_summary, error_recommendations
    
    def _format_json_for_ai(self, data: Dict[str, Any]) -> str:
        """
        Formázza a JSON adatokat AI számára - TELJES adathalmaz átadása
        """
        try:
            # Teljes JSON átadása - ne veszítsünk el adatokat
            if isinstance(data, list):
                full_data = data
            elif isinstance(data, dict) and 'results' in data:
                # Ha van results mező, azt és a meta információkat is küldjük
                full_data = {
                    "results": data['results'],
                    "analysis_metadata": {
                        "analysis_date": data.get("analysis_date"),
                        "enhancement_stats": data.get("enhancement_stats", {}),
                        "total_urls": len(data.get('results', [])) if data.get('results') else 0
                    }
                }
            else:
                full_data = data
            
            # Csak a hibás eredményeket szűrjük ki
            if isinstance(full_data, dict) and 'results' in full_data:
                full_data['results'] = [
                    item for item in full_data['results'] 
                    if isinstance(item, dict) and 'error' not in item
                ]
            elif isinstance(full_data, list):
                full_data = [
                    item for item in full_data 
                    if isinstance(item, dict) and 'error' not in item
                ]
            
            # Teljes JSON visszaadása - 8000 karakter limit a token korlátok miatt
            json_string = json.dumps(full_data, indent=2, ensure_ascii=False)
            
            # 8000 karakteres limit a GPT-4 token korlátok miatt
            if len(json_string) > 8000:
                logger.warning(f"Nagy JSON méret ({len(json_string)} karakter), limitálás 8000 karakterre")
                return json_string[:8000] + "\n... [truncated for token limit]"
            
            return json_string
            
        except Exception as e:
            logger.error(f"Hiba a JSON formázás során: {str(e)}")
            # Fallback: teljes adat string reprezentációja
            return str(data)[:8000]
    
    def _parse_ai_response_manually(self, response: str) -> Tuple[str, str]:
        """
        Manuális feldolgozás, ha az AI válasz nem valid JSON
        """
        try:
            # Próbáljuk megtalálni az összefoglalót és javaslatokat
            lines = response.split('\n')
            summary = ""
            recommendations = ""
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Keresés kulcsszavakra
                if any(keyword in line.lower() for keyword in ["összefoglaló", "summary", "áttekintés"]):
                    current_section = "summary"
                    continue
                elif any(keyword in line.lower() for keyword in ["javaslat", "recommendation", "tanács", "ajánlás"]):
                    current_section = "recommendations"
                    continue
                
                # Tartalom hozzáadása
                if current_section == "summary":
                    summary += line + " "
                elif current_section == "recommendations":
                    recommendations += line + " "
            
            # Ha nem találtunk semmit, osszuk fel a választ felezve
            if not summary and not recommendations:
                mid_point = len(response) // 2
                summary = response[:mid_point].strip()
                recommendations = response[mid_point:].strip()
            
            return summary.strip() or "Nem sikerült generálni az összefoglalót.", recommendations.strip() or "Nem sikerült generálni a javaslatokat."
            
        except Exception as e:
            logger.error(f"Hiba a manuális feldolgozás során: {str(e)}")
            return "Hiba történt a válasz feldolgozása során.", "Nem sikerült feldolgozni a javaslatokat."

def generate_ai_summary_from_file(json_file_path: str) -> Tuple[str, str]:
    """
    Segédfüggvény: AI összefoglaló generálása JSON fájlból
    
    Args:
        json_file_path: A JSON fájl elérési útja
        
    Returns:
        Tuple[str, str]: (összefoglaló, javaslatok)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        generator = AISummaryGenerator()
        return generator.generate_summary_and_recommendations(data)
        
    except FileNotFoundError:
        logger.error(f"JSON fájl nem található: {json_file_path}")
        return "A JSON fájl nem található.", "Kérlek, futtasd le előbb az elemzést."
    except Exception as e:
        logger.error(f"Hiba a fájl feldolgozása során: {str(e)}")
        return "Hiba történt a fájl feldolgozása során.", "Ellenőrizd a fájl formátumát és próbáld újra."

if __name__ == "__main__":
    # Teszt futtatás
    test_data = {
        "url": "https://example.com",
        "ai_readiness_score": 75.5,
        "meta_data": {"title": "Test Title", "description": "Test Description"},
        "content_quality": {"word_count": 500, "readability_score": 80}
    }
    
    try:
        generator = AISummaryGenerator()
        summary, recommendations = generator.generate_summary_and_recommendations(test_data)
        print("Összefoglaló:", summary)
        print("\nJavaslatok:", recommendations)
    except Exception as e:
        print(f"Teszt hiba: {str(e)}")
