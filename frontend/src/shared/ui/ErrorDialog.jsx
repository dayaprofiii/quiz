export default function ErrorDialog({ message, onClose }) {
  return (
    <div className="error-overlay">
      <div className="error-modal">
        <h1>ОШИБКА</h1>
        <p>{message || 'Не удалось выполнить действие. Проверьте данные и попробуйте снова.'}</p>
        <button onClick={onClose}>OK</button>
      </div>
    </div>
  );
}
