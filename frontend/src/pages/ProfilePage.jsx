import { useState } from 'react';
import { api } from '../shared/api/client.js';

function ProfileSetting({ title, children }) {
  return (
    <article className="grid min-h-[94px] grid-cols-[210px_1fr] overflow-hidden rounded-[10px] bg-quiz-panel max-[520px]:grid-cols-1">
      <div className="grid place-items-start p-5 text-sm text-quiz-text">{title}</div>
      <div className="grid content-center gap-2 bg-quiz-panelAlt px-6 py-3">{children}</div>
    </article>
  );
}

export default function ProfilePage({ user, onLogout, onUpdate, onError }) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [passwords, setPasswords] = useState({ current: '', next: '' });
  const [status, setStatus] = useState('');

  async function updateProfile(body, cleanup) {
    setStatus('');
    try {
      const data = await api(`/users/${user.id}`, { method: 'PUT', body });
      onUpdate(data.user);
      localStorage.setItem('quizleet:user', JSON.stringify(data.user));
      setStatus('Изменения сохранены');
      cleanup?.();
    } catch (err) {
      onError(err.message);
    }
  }

  function updateEmail() {
    const nextEmail = email.trim();
    if (!nextEmail) {
      onError('Введите новый адрес электронной почты.');
      return;
    }
    updateProfile({ email: nextEmail }, () => setEmail(''));
  }

  function updateName() {
    const nextName = name.trim();
    if (!nextName) {
      onError('Введите новое имя пользователя.');
      return;
    }
    updateProfile({ name: nextName }, () => setName(''));
  }

  function updatePassword() {
    const currentPassword = passwords.current.trim();
    const nextPassword = passwords.next.trim();
    if (!currentPassword || !nextPassword) {
      onError('Введите текущий и новый пароль.');
      return;
    }
    updateProfile({ currentPassword, nextPassword }, () => setPasswords({ current: '', next: '' }));
  }

  const fieldClass = 'mx-auto min-h-6 w-[150px] rounded bg-quiz-field px-2 py-1 text-[11px] text-quiz-fieldText';
  const currentFieldClass = 'mx-auto min-h-6 w-[150px] rounded bg-quiz-profileCurrent px-2 py-1 text-[11px] text-quiz-profileCurrentText';

  return (
    <section className="mx-auto grid min-h-[calc(100vh-116px)] w-full max-w-6xl content-start justify-items-center px-8 pt-20">
      <h1 className="text-shadow-quiz mb-12 text-2xl font-medium text-quiz-text">Управление учётной записью</h1>
      <div className="grid w-[min(100%,520px)] gap-5">
        <ProfileSetting title="Электронная почта">
          <input className={currentFieldClass} value={user.email} readOnly />
          <input className={fieldClass} placeholder="Новый адрес" value={email} onChange={(event) => setEmail(event.target.value)} />
          <button className={fieldClass} onClick={updateEmail}>Подтвердить</button>
        </ProfileSetting>
        <ProfileSetting title="Имя пользователя">
          <input className={currentFieldClass} value={user.name} readOnly />
          <input className={fieldClass} placeholder="Новое имя" value={name} onChange={(event) => setName(event.target.value)} />
          <button className={fieldClass} onClick={updateName}>Подтвердить</button>
        </ProfileSetting>
        <ProfileSetting title="Смена пароля">
          <input className={fieldClass} type="password" placeholder="Текущий пароль" value={passwords.current} onChange={(event) => setPasswords({ ...passwords, current: event.target.value })} />
          <input className={fieldClass} type="password" placeholder="Новый пароль" value={passwords.next} onChange={(event) => setPasswords({ ...passwords, next: event.target.value })} />
          <button className={fieldClass} onClick={updatePassword}>Подтвердить</button>
        </ProfileSetting>
      </div>
      {status && <p className="mt-5 text-sm text-green-300">{status}</p>}
      <button className="mt-7 w-[120px] rounded-md bg-quiz-danger px-4 py-2 text-xs font-bold text-white" onClick={onLogout}>Выйти</button>
    </section>
  );
}
