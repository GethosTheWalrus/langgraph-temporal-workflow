from datetime import timedelta
from temporalio import workflow

@workflow.defn
class SayHello:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            "say_hello", name, start_to_close_timeout=timedelta(seconds=5)
        )