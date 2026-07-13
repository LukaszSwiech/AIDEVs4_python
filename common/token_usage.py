from dataclasses import dataclass

@dataclass
class TokenUsage:
    input: int = 0
    output: int = 0
    cached: int = 0

    def add(self, usage) -> None:
        self.input += usage.input_tokens
        self.output += usage.output_tokens
        self.cached += usage.input_tokens_details.cached_tokens

    def log_total(self) -> None:
        pct = self.cached / self.input * 100 if self.input else 0
        print(f"""Tokens total summary:
              - input: {self.input} (cached: {self.cached} {pct:.0f}%),
              - output: {self.output}""")