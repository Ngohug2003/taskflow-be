class StringHelper:
    @staticmethod
    def escape_special_character_in_like_filter(value: str) -> str:
        return value.replace("%", "\\%").replace("_", "\\_")

    @staticmethod
    def str_to_models(table_name: str):
        # Placeholder for dynamic model loading if needed
        return None
