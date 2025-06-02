


type ChatbotWidgetProps = {
  onClick: () => void;
  icon?: string;
  label?: string;
};

const ChatbotWidget = ({ onClick, icon = '💬', label = '' }: ChatbotWidgetProps) => (
  <div
    onClick={onClick}
    className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg cursor-pointer hover:bg-blue-700 transition flex items-center gap-2"
  >
    <span>{icon}</span>
    {label && <span className="hidden sm:inline">{label}</span>}
  </div>
);

export default ChatbotWidget;

