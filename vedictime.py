from datetime import datetime, timedelta
import math
import ephem  # We'll use PyEphem for accurate sunrise/sunset times

class VedicDateTime:
    def __init__(self, date=None, lat=0, lon=0):
        self.date = date or datetime.now()
        self.lat = lat
        self.lon = lon
        self.observer = self._setup_observer()
        
        # Constants
        self.ayanamsa = 23.15  # Lahiri ayanamsa for current period
        self.tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        self.nakshatra_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
            "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
            "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
            "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        self.masa_names = [
            "Chaitra", "Vaisakha", "Jyeshtha", "Ashadha", "Shravana",
            "Bhadrapada", "Ashwina", "Kartika", "Margashirsha", "Pausha",
            "Magha", "Phalguna"
        ]
        self.solar_masa_names = [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha",
            "Kanya", "Tula", "Vrischika", "Dhanu", "Makara",
            "Kumbha", "Meena"
        ]
        self.rutu_names = [
            "Vasantha", "Grishma", "Varsha",
            "Sharad", "Hemanta", "Shishira"
        ]
        self.samvatsara_names = [
            "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
            "Angirasa", "Srimukha", "Bhava", "Yuva", "Dhatri",
            "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
            "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
            "Sarvajit", "Sarvadhari", "Virodhi", "Vikruti", "Khara",
            "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
            "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava",
            "Shubhakrut", "Shobhana", "Krodhi", "Vishvavasu", "Parabhava",
            "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrut",
            "Paridhavi", "Pramadicha", "Ananda", "Rakshasa", "Nala",
            "Pingala", "Kalayukti", "Siddharthi", "Raudra", "Durmati",
            "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
        ]
        self.karana_names = [
            "Bava", "Balava", "Kaulava", "Taitila", "Garija",
            "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga"
        ]
        self.yoga_names = [
            "Vishkhamba", "Preeti", "Ayushmaan", "Saubhaagya", "Sobhana",
            "Atiganda", "Sukarman", "Dhriti", "Shoola", "Ganda",
            "Vriddhi", "Dhruva", "Vyaaghaata", "Harshana", "Vajra",
            "Siddhi", "Vyatipaata", "Variyan", "Parigha", "Shiva",
            "Siddha", "Saadhya", "Subha", "Sukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        
    def _setup_observer(self):
        observer = ephem.Observer()
        observer.lat = str(self.lat)
        observer.lon = str(self.lon)
        observer.date = self.date
        return observer
    
    def get_sunrise_sunset(self):
        """Calculate sunrise and sunset times"""
        sun = ephem.Sun()
        sunrise = self.observer.next_rising(sun).datetime()
        sunset = self.observer.next_setting(sun).datetime()
        return sunrise, sunset
    
    def get_ayana(self):
        """Determine Uttarayana or Dakshinayana"""
        sun_long = self._sun_position()
        return "Uttara" if 0 <= sun_long <= 180 else "Dakshina"
    
    def get_arke(self):
        """Calculate Arke (solar day)"""
        sun_long = self._sun_position()
        arke = int(sun_long / 30) + 1
        return {
            "number": arke,
            "rashi": self.masa_names[(arke - 1) % 12]
        }
    
    def _calculate_end_time(self, start_time, unit_size):
        """Calculate end time based on unit size"""
        return start_time + timedelta(hours=unit_size)
    
    def _julian_day(self):
        """Convert date to Julian Day"""
        a = (14 - self.date.month) // 12
        y = self.date.year + 4800 - a
        m = self.date.month + 12 * a - 3
        jd = (self.date.day + ((153 * m + 2) // 5) + 365 * y + y // 4 
              - y // 100 + y // 400 - 32045)
        return jd + (self.date.hour - 12) / 24.0
    
    def _sun_position(self):
        """Calculate sun's position (simplified)"""
        jd = self._julian_day()
        n = jd - 2451545.0
        L = 280.460 + 0.9856474 * n  # Mean longitude
        g = 357.528 + 0.9856003 * n  # Mean anomaly
        
        # Simplified equation of center
        lambda_sun = L + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
        
        # Apply ayanamsa for sidereal position
        return (lambda_sun - self.ayanamsa) % 360
    
    def _moon_position(self):
        """Calculate moon's position (simplified)"""
        jd = self._julian_day()
        n = jd - 2451545.0
        
        # Simplified lunar position
        L = 218.316 + 13.176396 * n  # Mean longitude
        M = 134.963 + 13.064993 * n  # Mean anomaly
        F = 93.272 + 13.229350 * n   # Argument of latitude
        
        longitude = L + 6.289 * math.sin(math.radians(M))
        
        # Apply ayanamsa for sidereal position
        return (longitude - self.ayanamsa) % 360
    
    def get_tithi(self):
        """Calculate tithi with start/end times"""
        moon = self._moon_position()
        sun = self._sun_position()
        
        angle = (moon - sun) % 360
        tithi_num = int(angle / 12) + 1
        paksha = "Shukla" if tithi_num <= 15 else "Krishna"
        
        sunrise, _ = self.get_sunrise_sunset()
        # Approximate tithi duration (actual calculation would be more complex)
        tithi_duration = 24 * (angle % 12) / 12
        
        return {
            "number": tithi_num,
            "name": f"{paksha} {self.tithi_names[(tithi_num - 1) % 30]}",
            "paksha": paksha,
            "start_time": sunrise.isoformat(),
            "end_time": self._calculate_end_time(sunrise, tithi_duration).isoformat()
        }
    
    def get_nakshatra(self):
        """Calculate nakshatra with start/end times"""
        moon = self._moon_position()
        nakshatra_num = int(moon * 27 / 360) + 1
        
        sunrise, _ = self.get_sunrise_sunset()
        # Approximate nakshatra duration
        nakshatra_duration = 24 * (moon % (360/27)) / (360/27)
        
        return {
            "number": nakshatra_num,
            "name": self.nakshatra_names[nakshatra_num - 1],
            "start_time": sunrise.isoformat(),
            "end_time": self._calculate_end_time(sunrise, nakshatra_duration).isoformat()
        }
    
    def get_yoga(self):
        """Calculate yoga"""
        moon = self._moon_position()
        sun = self._sun_position()
        yoga_angle = (moon + sun) % 360
        yoga_num = int(yoga_angle * 27 / 360) + 1
        
        return {
            "number": yoga_num,
            "name": self.yoga_names[yoga_num - 1]
        }
    
    def get_karana(self):
        """Calculate karana"""
        moon = self._moon_position()
        sun = self._sun_position()
        angle = (moon - sun) % 360
        karana_num = (int(angle / 6) % 60) + 1
        
        return {
            "number": karana_num,
            "name": self.karana_names[karana_num % 10]
        }
    
    def get_masa(self):
        """Calculate lunar month"""
        sun = self._sun_position()
        masa_num = int(sun * 12 / 360)
        
        return {
            "number": masa_num + 1,
            "name": self.masa_names[masa_num],
            "is_adhika": False  # Simplified, actual calculation needs more parameters
        }

    def get_samvatsara(self):
        """Calculate samvatsara using Drik Ganita method"""
        # Constants
        SIDEREAL_YEAR = 365.25636
        KALI_EPOCH = 588465.5  # Julian day of Kali epoch

        # Convert date to Julian day
        jd = ephem.Date(self.date).real + 2415020  # Convert PyEphem date to Julian day

        # Get masa number (1-12)
        masa = self.get_masa()
        masa_num = masa["number"]

        # Calculate ahargana (elapsed days since Kali epoch)
        ahar = jd - KALI_EPOCH

        # Calculate Kali year
        kali = int((ahar + (4 - masa_num) * 30) / SIDEREAL_YEAR)

        # Apply corrections for current era
        if kali >= 4009:
            kali = (kali - 14) % 60

        # Calculate samvatsara number (1-60)
        samvat = (kali + 27 + int((kali * 211 - 108)/18000)) % 60
        if samvat == 0:
            samvat = 60

        return {
            "name": self.samvatsara_names[samvat - 1],
            "number": samvat
        }

    def get_rutu(self):
        """Calculate the Rutu (season) based on solar month"""
        solar_month = self._get_solar_month()
        rutu_index = (solar_month // 2) % 6
        return {
            "name": self.rutu_names[rutu_index],
            "number": rutu_index + 1
        }

    def _get_solar_month(self):
        """Get the solar month (0-11) based on sun's position"""
        sun_long = self._sun_position()
        return int(sun_long / 30) % 12

    def get_solar_masa(self):
        """Get the solar month name and number"""
        solar_month = self._get_solar_month()
        return {
            "name": self.solar_masa_names[solar_month],
            "number": solar_month + 1
        }

def get_panchanga(date=None, lat=0, lon=0):
    """Get complete panchanga for given date and location"""
    vdt = VedicDateTime(date, lat, lon)
    sunrise, sunset = vdt.get_sunrise_sunset()
    
    return {
        "tithi": vdt.get_tithi(),
        "nakshatra": vdt.get_nakshatra(),
        "masa": vdt.get_masa(),
        "yoga": vdt.get_yoga(),
        "karana": vdt.get_karana(),
        "samvatsara": vdt.get_samvatsara(),
        "rutu": vdt.get_rutu(),
        "solar_masa": vdt.get_solar_masa(),
        "ayana": vdt.get_ayana(),
        "arke": vdt.get_arke(),
        "sunrise": sunrise.isoformat(),
        "sunset": sunset.isoformat()
    } 