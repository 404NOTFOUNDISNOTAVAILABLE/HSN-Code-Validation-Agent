from app.validators import HSNValidator


class HSNValidationAgent:
    """
    Agent class for validating HSN codes using ADK framework components
    
    This agent handles the validation of HSN codes by leveraging the validator
    module and implementing the agent interface expected by the ADK framework.
    """
    
    def __init__(self):
        """Initialize the agent with the HSN validator"""
        self.validator = HSNValidator()
    
    def process_input(self, input_data):
        """
        Process input data from the user or system
        
        Args:
            input_data (dict): Input data containing HSN codes and options
            
        Returns:
            dict: Processed validation results
        """
        # Extract HSN codes from input
        hsn_codes = input_data.get("hsn_codes", [])
        include_hierarchy = input_data.get("include_hierarchy", False)
        
        # Handle different input formats
        if isinstance(hsn_codes, str):
            # If input is a single string, split by commas or newlines
            if "," in hsn_codes:
                hsn_codes = [code.strip() for code in hsn_codes.split(",")]
            elif "\n" in hsn_codes:
                hsn_codes = [code.strip() for code in hsn_codes.split("\n")]
            else:
                # Single code as string
                hsn_codes = [hsn_codes.strip()]
        
        # Filter out empty codes
        hsn_codes = [code for code in hsn_codes if code.strip()]
        
        if not hsn_codes:
            return {
                "success": False,
                "error": "No valid HSN codes provided"
            }
        
        # Process single code or multiple codes
        if len(hsn_codes) == 1:
            result = self.validator.validate_hsn_code(hsn_codes[0], include_hierarchy)
            return {
                "success": True,
                "single_result": True,
                "result": result
            }
        else:
            results = self.validator.validate_hsn_codes(hsn_codes, include_hierarchy)
            return {
                "success": True,
                "single_result": False,
                "results": results
            }
    
    def handle_intent(self, intent, entities=None):
        """
        Handle different user intents in a conversational context
        
        Args:
            intent (str): The identified user intent
            entities (dict): Extracted entities from user input
            
        Returns:
            dict: Response based on intent handling
        """
        if intent == "validate_hsn":
            # Handle HSN validation intent
            hsn_codes = entities.get("hsn_codes", [])
            include_hierarchy = entities.get("include_hierarchy", False)
            
            input_data = {
                "hsn_codes": hsn_codes,
                "include_hierarchy": include_hierarchy
            }
            
            return self.process_input(input_data)
            
        elif intent == "get_hsn_info":
            # Handle getting HSN info intent
            hsn_code = entities.get("hsn_code")
            if not hsn_code:
                return {
                    "success": False,
                    "error": "No HSN code provided"
                }
                
            result = self.validator.validate_hsn_code(hsn_code, include_hierarchy=True)
            return {
                "success": True,
                "result": result
            }
            
        elif intent == "help":
            # Handle help intent
            return {
                "success": True,
                "message": "I can help you validate HSN codes. Simply provide me with one or more codes to validate."
            }
            
        else:
            # Handle unknown intent
            return {
                "success": False,
                "error": "I don't understand that request. Try asking me to validate an HSN code."
            }
    
    def format_response(self, processing_result):
        """
        Format the validation results into a user-friendly response
        
        Args:
            processing_result (dict): Result from process_input or handle_intent
            
        Returns:
            dict: Formatted response for the user
        """
        if not processing_result.get("success"):
            return {
                "response_type": "error",
                "message": processing_result.get("error", "An error occurred during processing")
            }
        
        if processing_result.get("single_result"):
            # Format single result
            result = processing_result["result"]
            if result["valid"]:
                response = {
                    "response_type": "valid_hsn",
                    "code": result["code"],
                    "description": result["description"],
                    "message": f"The HSN code {result['code']} is valid: {result['description']}"
                }
            else:
                response = {
                    "response_type": "invalid_hsn",
                    "code": result["code"],
                    "reason": result.get("reason", "Unknown reason"),
                    "message": f"The HSN code {result['code']} is invalid: {result.get('reason', 'Unknown reason')}"
                }
                
            # Add hierarchy information if available
            if "hierarchy_valid" in result:
                response["hierarchy_valid"] = result["hierarchy_valid"]
                response["parent_codes"] = result["parent_codes"]
                
                if not result["hierarchy_valid"]:
                    response["message"] += f". Additionally, some parent codes are invalid: {', '.join(result['parent_codes']['invalid'])}"
                
            return response
            
        else:
            # Format multiple results
            results = processing_result["results"]
            summary = f"Validated {results['total']} HSN codes: {results['valid_count']} valid, {results['invalid_count']} invalid"
            
            response = {
                "response_type": "multiple_hsn_results",
                "summary": summary,
                "valid_count": results["valid_count"],
                "invalid_count": results["invalid_count"],
                "total": results["total"],
                "results": results["results"]
            }
            
            return response