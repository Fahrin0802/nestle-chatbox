// import React, { useState } from 'react';
// import ChatbotWidget from './components/ChatbotWidget';
// import ChatWindow from './components/ChatWindow';

// function App() {
//   const [open, setOpen] = useState(false);

//   return (
//     <div
//       className="min-h-screen bg-cover bg-center"
//       style={{ backgroundImage: "url('/nestle-screenshot.png')" }}
//     >
//       {open ? (
//         <ChatWindow onClose={() => setOpen(false)} />
//       ) : (
//         <ChatbotWidget onClick={() => setOpen(true)} />
//       )}
//     </div>
//   );
  
// }

// export default App;

import { useState } from 'react';
import ChatbotWidget from './components/ChatbotWidget';
import ChatWindow from './components/ChatWindow';

function App() {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="min-h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/nestle-screenshot.png')" }}
    >
      {open ? (
        <ChatWindow onClose={() => setOpen(false)} />
      ) : (
        <ChatbotWidget
          onClick={() => setOpen(true)}
          icon="🤖"
          label="Ask Nestlé"
        />
      )}
    </div>
  );
}

export default App;

