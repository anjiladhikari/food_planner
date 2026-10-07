import { useState } from "react";

export default function RagChat() {
  const [open, setOpen] = useState(false);

  // Chat state
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    // Show user's message immediately
    setMessages((current) => [
      ...current,
      {
        role: "user",
        text: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("https://food-planner-iba3.onrender.com/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();
      // Find which sources the LLM actually cited, e.g. [Source 1]
      const citedNumbers = new Set(
        [...data.answer.matchAll(/\[Source\s+(\d+)\]/g)].map(
          (match) => Number(match[1])
        )
      );

      const citedSources = data.sources
        .map((source, index) => ({
          ...source,
          sourceNumber: index + 1,
        }))
        .filter((source) => citedNumbers.has(source.sourceNumber));
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: data.answer,
          sources: citedSources,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: "Sorry, I couldn't reach the assistant.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className="rag-chat-button"
        aria-expanded={open}
        aria-label={open ? "Close assistant" : "Open assistant"}
        onClick={() => setOpen((current) => !current)}
      >
        Ask
      </button>

      {open && (
        <div
          className="rag-chat-panel"
          role="dialog"
          aria-label="Food Planner Assistant"
        >
          <div className="rag-chat-header">
            <h2 className="rag-chat-title">
              Food Planner Assistant
            </h2>

            <button
              type="button"
              className="rag-chat-close"
              aria-label="Close assistant"
              onClick={() => setOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="rag-chat-body">
            {messages.length === 0 && (
              <p className="rag-chat-intro">
                Ask me about the meal plan, shopping items, or cooking
                instructions.
              </p>
            )}

            <div className="rag-chat-messages">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`rag-chat-message ${message.role}`}
                >
                  <>
                    <div>{message.text}</div>

                    {message.role === "assistant" &&
                      message.sources?.length > 0 && (
                        <div className="rag-chat-sources">
                          <strong>Sources</strong>

                          {message.sources.map((source, sourceIndex) => (
                            <div key={source.chunk_id}>
                              [{source.sourceNumber}]{" "}
                              {source.metadata.food_item ||
                                source.metadata.day ||
                                source.chunk_id}
                              {" — "}
                              {source.metadata.source_type}
                            </div>
                          ))}
                        </div>
                      )}
                  </>
                </div>
              ))}
            </div>
          </div>

          <div className="rag-chat-input">
            <input
              type="text"
              placeholder="Type a question…"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />

            <button
              type="button"
              onClick={sendMessage}
              disabled={loading}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}