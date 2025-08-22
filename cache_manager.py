import json
import hashlib
import time
from typing import Optional, Dict, Any
import os
from pathlib import Path


class CacheManager:
    """Egyszerű fájl-alapú cache manager Redis helyett a könnyebb deployment érdekében"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = 3600  # 1 óra
        
    def get_cache_key(self, url: str, analysis_type: str, params: Dict = None) -> str:
        """Cache kulcs generálása"""
        key_data = {
            "url": url,
            "type": analysis_type,
            "params": params or {},
            "version": "2.0"  # verziókezelés
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Cache eredmény lekérése"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # TTL ellenőrzés
            if time.time() > cache_data.get('expires_at', 0):
                cache_file.unlink()  # Lejárt cache törlése
                return None
                
            return cache_data.get('result')
            
        except (json.JSONDecodeError, KeyError, OSError):
            # Hibás cache fájl törlése
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None
    
    def set_cached_result(self, cache_key: str, result: Dict, ttl: int = None) -> bool:
        """Eredmény cache-elése"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        ttl = ttl or self.default_ttl
        
        cache_data = {
            "result": result,
            "cached_at": time.time(),
            "expires_at": time.time() + ttl
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False
    
    def invalidate_url_cache(self, url: str) -> int:
        """URL-hez kapcsolódó cache fájlok törlése"""
        deleted_count = 0
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if url_hash in cache_file.name:
                    cache_file.unlink()
                    deleted_count += 1
            except OSError:
                pass
                
        return deleted_count
    
    def get_cache_stats(self) -> Dict:
        """Cache statisztikák"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        valid_count = 0
        expired_count = 0
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if time.time() > cache_data.get('expires_at', 0):
                    expired_count += 1
                else:
                    valid_count += 1
                    
            except (json.JSONDecodeError, KeyError, OSError):
                expired_count += 1
        
        return {
            "total_files": len(cache_files),
            "valid_files": valid_count,
            "expired_files": expired_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir)
        }
    
    def cleanup_expired(self) -> int:
        """Lejárt cache fájlok törlése"""
        deleted_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if time.time() > cache_data.get('expires_at', 0):
                    cache_file.unlink()
                    deleted_count += 1
                    
            except (json.JSONDecodeError, KeyError, OSError):
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except OSError:
                    pass
        
        return deleted_count
    
    def clear_all_cache(self) -> Dict:
        """Teljes cache mappa törlése"""
        import shutil
        
        if not self.cache_dir.exists():
            return {"deleted_files": 0, "deleted_dirs": 0, "status": "Cache mappa nem létezik"}
        
        deleted_files = 0
        deleted_dirs = 0
        
        try:
            # Először számoljuk meg mi van benne
            for cache_file in self.cache_dir.rglob("*"):
                if cache_file.is_file():
                    deleted_files += 1
                elif cache_file.is_dir():
                    deleted_dirs += 1
            
            # Teljes mappa törlése
            shutil.rmtree(self.cache_dir)
            
            # Újra létrehozzuk az üres mappát
            self.cache_dir.mkdir(exist_ok=True)
            
            return {
                "deleted_files": deleted_files,
                "deleted_dirs": deleted_dirs,
                "status": "success",
                "message": f"Teljes cache törölve: {deleted_files} fájl, {deleted_dirs} mappa"
            }
            
        except Exception as e:
            return {
                "deleted_files": 0,
                "deleted_dirs": 0,
                "status": "error",
                "message": f"Hiba a cache törlésekor: {str(e)}"
            }