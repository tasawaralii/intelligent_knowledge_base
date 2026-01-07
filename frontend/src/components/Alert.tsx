import { useAlert } from "../context/alertContext";

export const AlertContainer = () => {
  const { alerts, removeAlert } = useAlert();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {alerts.map(alert => (
        <div
          key={alert.id}
          className={`p-4 rounded-lg shadow-lg text-white flex justify-between items-center animate-fadeIn ${
            alert.type === "success"
              ? "bg-green-500"
              : alert.type === "error"
              ? "bg-red-500"
              : alert.type === "warning"
              ? "bg-yellow-500"
              : "bg-blue-500"
          }`}
        >
          <span>{alert.message}</span>
          <button
            onClick={() => removeAlert(alert.id)}
            className="ml-4 font-bold hover:opacity-80 transition-opacity"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};
