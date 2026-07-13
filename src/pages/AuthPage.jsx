import { useState } from 'react';
import { api } from '../shared/api/client.js';

const authInputClass = 'rounded bg-quiz-field px-3 py-2 text-xs text-quiz-fieldText';
const authButtonClass = 'rounded-md bg-quiz-primary px-4 py-2 text-xs font-bold text-white';

export default function AuthPage({ mode, onSwitch, onDone, onError }) {
  const [form, setForm] = useState({ email: mode === 'login' ? 'organizer@quiz.test' : '', name: '', password: mode === 'login' ? '123456' : '' });
  const register = mode === 'register';

  async function submit(event) {
    event.preventDefault();
    try {
      const data = await api(`/auth/${register ? 'register' : 'login'}`, { method: 'POST', body: form });
      onDone(data.user);
    } catch (err) {
      onError(err.message);
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-116px)] w-full max-w-6xl flex-col items-center px-8 py-14">
      <form className="mt-28 grid w-[min(100%,300px)] gap-3 rounded-lg bg-quiz-panel px-7 py-6 shadow-2xl" onSubmit={submit}>
        <h1 className="mb-2 text-center text-lg font-medium">{register ? 'Регистрация аккаунта' : 'Авторизация'}</h1>
        <input className={authInputClass} placeholder="Электронная почта" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
        {register && <input className={authInputClass} placeholder="Имя пользователя" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />}
        <input className={authInputClass} placeholder="Пароль" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />
        <button className={authButtonClass} type="submit">{register ? 'РЕГИСТРАЦИЯ' : 'ВОЙТИ'}</button>
        <button className="bg-transparent p-1 text-[10px] font-bold text-white" type="button" onClick={onSwitch}>{register ? 'Уже есть аккаунт' : 'Нет аккаунта? Регистрация'}</button>
      </form>
    </section>
  );
}
