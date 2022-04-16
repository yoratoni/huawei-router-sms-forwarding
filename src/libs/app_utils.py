class AppUtils:
    @staticmethod
    def string_list_to_list(input: str) -> list:
        """Converts a string representation of a list
        coming from an .env file to a real Python list.
        
        Note:
            If the string representation of the list is invalid, returns an empty list.

        Args:
            input (str): The default string list.

        Returns:
            list: A python list.
        """
        
        output = []
        
        if "[" in input and "]" in input:
            output = input.strip("][").split(", ")
            
        for i, elem in enumerate(output):
            single = (elem[0] == "'" and elem[-1] == "'")
            double = (elem[0] == '"' and elem[-1] == '"')
            
            if single or double:
                output[i] = elem[1:-1]

        return output
        