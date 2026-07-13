import { useState } from 'react';
import { normalizeCode } from '../shared/lib/quiz.js';

export default function MainPage({ onJoin, onLogin, user }) {
  const [code, setCode] = useState('');

  function submit() {
    if (!user) {
      onLogin();
      return;
    }
    onJoin(code);
  }

  return (
    <section className="page main-page">
      <p className="main-title">Онлайн-викторины на любую тематику</p>
      <p className="main-description">
        Составляйте и запускайте собственные квизы, либо же попробуйте себя в роли участника
        в борьбе с другими участниками
      </p>
      <label className="main-code-label">
        ВВЕДИТЕ КОД ВИКТОРИНЫ
        <input className="main-code-input" value={code} onChange={(event) => setCode(normalizeCode(event.target.value))} />
      </label>
      <button className="main-join-button" onClick={submit}>
        ПРИСОЕДИНИТЬСЯ К ВИКТОРИНЕ
      </button>
    </section>
  );
}
