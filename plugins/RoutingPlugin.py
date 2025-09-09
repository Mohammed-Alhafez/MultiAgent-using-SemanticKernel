from semantic_kernel.functions import kernel_function

class RoutingPlugin:
    @kernel_function(name="route_to_db", description="Route the input to the DBAgent.")
    def route_to_db(self) -> str:
        return "DBAgent"

    @kernel_function(name="route_to_info", description="Route the input to the InformativeAgent.")
    def route_to_info(self) -> str:
        return "InformativeAgent"
