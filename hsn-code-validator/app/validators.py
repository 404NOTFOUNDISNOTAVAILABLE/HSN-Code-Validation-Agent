from app.data_handler import HSNDataHandler


class HSNValidator:
    """
    Validates HSN codes based on format and existence in the master data
    """
    
    def __init__(self):
        """Initialize the validator with data handler"""
        self.data_handler = HSNDataHandler()
    
    def validate_format(self, hsn_code):
        """
        Validate the format of an HSN code
        
        Args:
            hsn_code (str): The HSN code to validate
            
        Returns:
            dict: Validation result with status and reason
        """
        hsn_code = str(hsn_code).strip()
        
        # Check if the code is not empty
        if not hsn_code:
            return {
                "valid": False,
                "reason": "HSN code cannot be empty"
            }
        
        # Check if the code contains only digits
        if not hsn_code.isdigit():
            return {
                "valid": False,
                "reason": "HSN code must contain only digits"
            }
        
        # Check if the code length is valid (based on observed data)
        if len(hsn_code) not in self.data_handler.valid_lengths:
            return {
                "valid": False,
                "reason": f"Invalid HSN code length. Valid lengths are: {sorted(self.data_handler.valid_lengths)}"
            }
        
        return {"valid": True}
    
    def validate_existence(self, hsn_code):
        """
        Check if the HSN code exists in the master data
        
        Args:
            hsn_code (str): The HSN code to validate
            
        Returns:
            dict: Validation result with status and description if valid
        """
        hsn_code = str(hsn_code).strip()
        
        if self.data_handler.is_valid_code(hsn_code):
            return {
                "valid": True,
                "description": self.data_handler.get_description(hsn_code)
            }
        else:
            return {
                "valid": False,
                "reason": "HSN code not found in master data"
            }
    
    def validate_hierarchy(self, hsn_code):
        """
        Validate the hierarchical structure of an HSN code
        
        Args:
            hsn_code (str): The HSN code to validate
            
        Returns:
            dict: Hierarchical validation results
        """
        return self.data_handler.validate_parent_hierarchy(hsn_code)
    
    def validate_hsn_code(self, hsn_code, include_hierarchy=False):
        """
        Complete validation of an HSN code
        
        Args:
            hsn_code (str): The HSN code to validate
            include_hierarchy (bool): Whether to include hierarchical validation
            
        Returns:
            dict: Complete validation results
        """
        hsn_code = str(hsn_code).strip()
        
        # Start with format validation
        format_result = self.validate_format(hsn_code)
        if not format_result["valid"]:
            return {
                "code": hsn_code,
                "valid": False,
                "format_valid": False,
                "reason": format_result["reason"]
            }
        
        # Then validate existence
        existence_result = self.validate_existence(hsn_code)
        
        result = {
            "code": hsn_code,
            "valid": existence_result["valid"],
            "format_valid": True
        }
        
        if existence_result["valid"]:
            result["description"] = existence_result["description"]
        else:
            result["reason"] = existence_result["reason"]
        
        # Add hierarchical validation if requested
        if include_hierarchy and len(hsn_code) > 2:
            hierarchy_result = self.validate_hierarchy(hsn_code)
            result["hierarchy_valid"] = hierarchy_result["valid"]
            result["parent_codes"] = {
                "valid": hierarchy_result["valid_parents"],
                "invalid": hierarchy_result["invalid_parents"]
            }
        
        return result
    
    def validate_hsn_codes(self, hsn_codes, include_hierarchy=False):
        """
        Validate multiple HSN codes
        
        Args:
            hsn_codes (list): List of HSN codes to validate
            include_hierarchy (bool): Whether to include hierarchical validation
            
        Returns:
            dict: Validation results for all codes
        """
        results = {
            "total": len(hsn_codes),
            "valid_count": 0,
            "invalid_count": 0,
            "results": []
        }
        
        for code in hsn_codes:
            result = self.validate_hsn_code(code, include_hierarchy)
            results["results"].append(result)
            
            if result["valid"]:
                results["valid_count"] += 1
            else:
                results["invalid_count"] += 1
        
        return results