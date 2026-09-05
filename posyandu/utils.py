from datetime import date
from typing import Dict, List, Tuple

class ImmunizationAgeFilter:
    """Utility class for filtering immunizations by age and vaccine type"""
    
    # Vaccine age requirements in months
    VACCINE_AGE_REQUIREMENTS = {
        'bcg': (0, 1),  # BCG: 0-1 month
        'hepatitis': (0, 1),  # Hepatitis B: 0-1 month
        'polio': (0, 2),  # Polio: 0-2 months
        'dpt': (2, 6),  # DPT: 2-6 months
        'campak': (9, 12),  # Campak: 9-12 months
        'other': (0, 60),  # Other vaccines: 0-60 months
    }
    
    @classmethod
    def get_eligible_vaccines(cls, age_months: int) -> List[str]:
        """Get list of vaccines eligible for given age in months"""
        eligible = []
        for vaccine, (min_age, max_age) in cls.VACCINE_AGE_REQUIREMENTS.items():
            if min_age <= age_months <= max_age:
                eligible.append(vaccine)
        return eligible
    
    @classmethod
    def get_age_range_for_vaccine(cls, vaccine_type: str) -> Tuple[int, int]:
        """Get age range for specific vaccine type"""
        return cls.VACCINE_AGE_REQUIREMENTS.get(vaccine_type, (0, 60))
    
    @classmethod
    def is_vaccine_eligible(cls, vaccine_type: str, age_months: int) -> bool:
        """Check if vaccine is eligible for given age"""
        min_age, max_age = cls.get_age_range_for_vaccine(vaccine_type)
        return min_age <= age_months <= max_age
    
    @classmethod
    def get_vaccine_schedule(cls) -> Dict[str, Dict]:
        """Get complete vaccination schedule"""
        return {
            'bcg': {
                'name': 'BCG',
                'age_range': '0-1 bulan',
                'description': 'Vaksin untuk mencegah TBC',
                'priority': 'High',
                'color': 'success'
            },
            'hepatitis': {
                'name': 'Hepatitis B',
                'age_range': '0-1 bulan',
                'description': 'Vaksin untuk mencegah Hepatitis B',
                'priority': 'High',
                'color': 'info'
            },
            'polio': {
                'name': 'Polio',
                'age_range': '0-2 bulan',
                'description': 'Vaksin untuk mencegah Polio',
                'priority': 'High',
                'color': 'warning'
            },
            'dpt': {
                'name': 'DPT',
                'age_range': '2-6 bulan',
                'description': 'Vaksin untuk mencegah Difteri, Pertusis, Tetanus',
                'priority': 'High',
                'color': 'danger'
            },
            'campak': {
                'name': 'Campak',
                'age_range': '9-12 bulan',
                'description': 'Vaksin untuk mencegah Campak',
                'priority': 'Medium',
                'color': 'primary'
            },
            'other': {
                'name': 'Lainnya',
                'age_range': '0-60 bulan',
                'description': 'Vaksin tambahan lainnya',
                'priority': 'Low',
                'color': 'secondary'
            }
        }
    
    @classmethod
    def filter_immunizations_by_age(cls, immunizations, age_months: int):
        """Filter immunizations by age eligibility"""
        eligible_vaccines = cls.get_eligible_vaccines(age_months)
        return immunizations.filter(vaccine_type__in=eligible_vaccines)
    
    @classmethod
    def get_missing_vaccines(cls, age_months: int, completed_vaccines: List[str]) -> List[str]:
        """Get list of missing vaccines for given age"""
        eligible_vaccines = cls.get_eligible_vaccines(age_months)
        return [v for v in eligible_vaccines if v not in completed_vaccines]
    
    @classmethod
    def get_next_due_vaccines(cls, age_months: int) -> List[str]:
        """Get next vaccines due based on age"""
        next_vaccines = []
        for vaccine, (min_age, max_age) in cls.VACCINE_AGE_REQUIREMENTS.items():
            if age_months >= min_age and age_months <= max_age:
                next_vaccines.append(vaccine)
        return next_vaccines

def calculate_age_in_months(birth_date: date, current_date: date = None) -> int:
    """Calculate age in months from birth date"""
    if current_date is None:
        current_date = date.today()
    
    years = current_date.year - birth_date.year
    months = current_date.month - birth_date.month
    
    if current_date.day < birth_date.day:
        months -= 1
    
    return years * 12 + months

def get_immunization_status(patient_age_months: int, completed_vaccines: List[str]) -> Dict:
    """Get comprehensive immunization status for a patient"""
    filter_util = ImmunizationAgeFilter()
    
    eligible_vaccines = filter_util.get_eligible_vaccines(patient_age_months)
    missing_vaccines = filter_util.get_missing_vaccines(patient_age_months, completed_vaccines)
    next_due = filter_util.get_next_due_vaccines(patient_age_months)
    
    return {
        'age_months': patient_age_months,
        'eligible_vaccines': eligible_vaccines,
        'completed_vaccines': completed_vaccines,
        'missing_vaccines': missing_vaccines,
        'next_due_vaccines': next_due,
        'completion_percentage': len(completed_vaccines) / len(eligible_vaccines) * 100 if eligible_vaccines else 0,
        'is_up_to_date': len(missing_vaccines) == 0
    }

def get_vaccine_recommendations(patient_age_months: int) -> List[Dict]:
    """Get vaccine recommendations based on age"""
    filter_util = ImmunizationAgeFilter()
    schedule = filter_util.get_vaccine_schedule()
    
    recommendations = []
    for vaccine_type, (min_age, max_age) in filter_util.VACCINE_AGE_REQUIREMENTS.items():
        if min_age <= patient_age_months <= max_age:
            vaccine_info = schedule.get(vaccine_type, {})
            recommendations.append({
                'vaccine_type': vaccine_type,
                'name': vaccine_info.get('name', vaccine_type.title()),
                'age_range': vaccine_info.get('age_range', f'{min_age}-{max_age} bulan'),
                'description': vaccine_info.get('description', ''),
                'priority': vaccine_info.get('priority', 'Medium'),
                'color': vaccine_info.get('color', 'secondary'),
                'is_eligible': True
            })
    
    return recommendations

