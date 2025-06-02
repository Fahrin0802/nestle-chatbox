// import React from 'react';

// const ChatWindow = ({ onClose }: { onClose: () => void }) => (
//   <div className="fixed bottom-4 right-4 w-80 h-96 bg-white shadow-xl rounded-lg flex flex-col border border-gray-300">
//     <div className="p-2 bg-blue-600 text-white rounded-t-lg flex justify-between items-center">
//       <span>Chat with Nestlé AI</span>
//       <button onClick={onClose} className="font-bold text-lg">×</button>
//     </div>
//     <div className="flex-1 p-4 overflow-y-auto">
//       <p>Hi! Ask me anything about Nestlé recipes or products 🍪</p>
//     </div>
//     <div className="p-2 border-t flex">
//       <input
//         type="text"
//         placeholder="Type your message..."
//         className="flex-1 border rounded p-2"
//       />
//       <button className="ml-2 px-4 py-2 bg-blue-600 text-white rounded">Send</button>
//     </div>
//   </div>
// );

// export default ChatWindow;


import React, { useState } from 'react';

// type ChatWindowProps = {
//   onClose: () => void;
// };
type ChatWindowProps = {
  onClose: () => void;
  title?: string; 
};

const ChatWindow: React.FC<ChatWindowProps> = ({ onClose }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer('');
    setSources([]);

    try {
      const res = await fetch('https://nestle-chatbot-1008554254081.us-central1.run.app/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setAnswer(data.answer || 'No answer found.');
      setSources(data.sources || []);
    } catch (err) {
      setAnswer('Error fetching response from backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-xl shadow-lg p-4 w-[350px] max-h-[90vh] flex flex-col space-y-2 overflow-y-auto">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold">Nestlé ChatBot</h2>
        <button onClick={onClose} className="text-red-500 font-bold">X</button>
      </div>

      <textarea
        className="border rounded p-2 w-full resize-none"
        rows={3}
        placeholder="Ask a question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button
        onClick={askQuestion}
        disabled={loading}
        className="bg-green-600 text-white py-1 px-3 rounded hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      {answer && (
        <div>
          <p className="font-medium text-gray-800">{answer}</p>
          {sources.length > 0 && (
            <div className="mt-2">
              <p className="text-sm font-semibold">Sources:</p>
              <ul className="list-disc list-inside text-blue-600 text-sm">
                {sources.map((src, idx) => (
                  <li key={idx}>
                    <a href={src} target="_blank" rel="noopener noreferrer">
                      {src}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;

