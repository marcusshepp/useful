import fetch from "node-fetch";

const prompt: string = `

@Component({
    selector: 'app-term-search',
    templateUrl: './term-search.component.html',
    styleUrls: ['./term-search.component.css'],
})
export class TermSearchComponent extends DestroyableComponent {

    constructor(
        private sessionStateService: SessionStateService,
    ) {
        super();
    }

    private get sessionId(): number {
        return this.sessionStateService.getCurrentSessionId();
    }

    private get sessionDayId(): number {
        return this.sessionStateService.getCurrentSessionDay().id;
    }
}
`;

interface OllamaResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
}

class OllamaClient {
  private readonly baseUrl: string;

  public constructor(baseUrl: string = "http://localhost:11434") {
    this.baseUrl = baseUrl;
  }

  public async generateResponse(
    prompt: string,
    model: string = "gemma3",
  ): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: model,
          prompt: prompt,
          stream: false,
        }),
      });

      const data = (await response.json()) as OllamaResponse;
      return data.response;
    } catch (error) {
      console.error("Error generating response:", error);
      throw error;
    }
  }
}

async function main(): Promise<void> {
  const client: OllamaClient = new OllamaClient();

  try {
    const response: string = await client.generateResponse(prompt);
    console.log(response);
  } catch (error) {
    console.error("Failed to get response:", error);
  }
}

main();
