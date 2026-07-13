import { useEffect, useMemo, useState } from 'react';
import { api } from '../shared/api/client.js';
import { roomWebSocketUrl } from '../shared/api/config.js';
import Layout from '../shared/ui/Layout.jsx';
import ErrorDialog from '../shared/ui/ErrorDialog.jsx';
import MainPage from '../pages/MainPage.jsx';
import AuthPage from '../pages/AuthPage.jsx';
import ProfilePage from '../pages/ProfilePage.jsx';
import QuizListPage from '../pages/QuizListPage.jsx';
import QuizEditorPage from '../pages/QuizEditorPage.jsx';
import OrganizerRoomPage from '../pages/OrganizerRoomPage.jsx';
import PlayRoomPage from '../pages/PlayRoomPage.jsx';
import HistoryPage from '../pages/HistoryPage.jsx';
import { normalizeCode, validateQuiz } from '../shared/lib/quiz.js';

const activeRoomKey = 'quizleet:activeRoom';

export default function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('quizleet:user') || 'null'));
  const [view, setView] = useState('home');
  const [quizzes, setQuizzes] = useState([]);
  const [history, setHistory] = useState([]);
  const [room, setRoom] = useState(null);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) localStorage.setItem('quizleet:user', JSON.stringify(user));
  }, [user]);

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!user) return;
    const saved = JSON.parse(localStorage.getItem(activeRoomKey) || 'null');
    if (!saved?.code || saved.userId !== user.id) return;
    api(`/rooms/${saved.code}`)
      .then((data) => {
        setRoom(data.room);
        setView(saved.view === 'room' ? 'room' : 'play');
      })
      .catch(() => localStorage.removeItem(activeRoomKey));
  }, [user?.id]);

  useEffect(() => {
    if (!room?.code) return undefined;
    const socket = new WebSocket(roomWebSocketUrl(room.code));
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'room') setRoom(message.room);
      if (message.type === 'error') setError(message.message);
    };
    socket.onerror = () => setError('Не удалось подключиться к комнате.');
    return () => socket.close();
  }, [room?.code]);

  useEffect(() => {
    if (!user || !room?.code || !['room', 'play'].includes(view)) return;
    localStorage.setItem(activeRoomKey, JSON.stringify({ code: room.code, view, userId: user.id }));
  }, [room?.code, user?.id, view]);

  useEffect(() => {
    if (!user || view !== 'room' || room?.status !== 'running' || room.organizerId !== user.id) return undefined;
    const delay = Math.max(0, Number(room.remainingSeconds || 0)) * 1000 + 500;
    const timer = window.setTimeout(() => {
      api(`/rooms/${room.code}/next`, { method: 'POST' })
        .then((data) => {
          setRoom(data.room);
          if (data.room.status === 'finished') refresh().catch((err) => setError(err.message));
        })
        .catch((err) => setError(err.message));
    }, delay);
    return () => window.clearTimeout(timer);
  }, [room?.code, room?.currentIndex, room?.remainingSeconds, room?.status, room?.organizerId, user?.id, view]);

  async function refresh() {
    const [quizData, historyData] = await Promise.all([api('/quizzes'), api('/history')]);
    setQuizzes(quizData.quizzes);
    setHistory(historyData.history);
  }

  function logout() {
    localStorage.removeItem('quizleet:user');
    localStorage.removeItem(activeRoomKey);
    setUser(null);
    setView('login');
    setRoom(null);
  }

  async function saveQuiz(quiz) {
    const validationError = validateQuiz(quiz);
    if (validationError) {
      setError(validationError);
      return null;
    }
    const payload = { ...quiz, title: quiz.title.trim(), ownerId: user.id };
    const data = quiz.id
      ? await api(`/quizzes/${quiz.id}`, { method: 'PUT', body: payload })
      : await api('/quizzes', { method: 'POST', body: payload });
    setEditing(null);
    setView('quizzes');
    await refresh();
    return data.quiz;
  }

  async function launchQuiz(quiz) {
    if (!quiz.questions?.length) {
      setError('Викторина должна содержать хотя бы один вопрос.');
      return;
    }
    const data = await api('/rooms', { method: 'POST', body: { quizId: quiz.id, organizerId: user.id } });
    setRoom(data.room);
    setView('room');
  }

  async function joinRoom(code) {
    const roomCode = normalizeCode(code);
    if (!roomCode) {
      setError('Введите код викторины.');
      return;
    }
    const data = await api(`/rooms/${roomCode}/join`, { method: 'POST', body: { userId: user?.id, name: user?.name || 'Player' } });
    setRoom(data.room);
    setView('play');
  }

  const ownedQuizzes = useMemo(() => quizzes.filter((quiz) => quiz.ownerId === user?.id), [quizzes, user]);

  return (
    <Layout user={user} setView={setView}>
      {error && <ErrorDialog message={error} onClose={() => setError('')} />}
      {view === 'home' && <MainPage onJoin={joinRoom} onLogin={() => setView('login')} user={user} />}
      {!user && view === 'login' && <AuthPage mode="login" onSwitch={() => setView('register')} onDone={(nextUser) => { setUser(nextUser); setView('quizzes'); }} onError={setError} />}
      {!user && view === 'register' && <AuthPage mode="register" onSwitch={() => setView('login')} onDone={(nextUser) => { setUser(nextUser); setView('quizzes'); }} onError={setError} />}
      {user && view === 'profile' && <ProfilePage user={user} onLogout={logout} onUpdate={setUser} onError={setError} />}
      {user && view === 'quizzes' && <QuizListPage quizzes={ownedQuizzes} onCreate={() => { setEditing({ title: '', category: 'Общее', timeLimit: 45, rules: '', questions: [] }); setView('editor'); }} onEdit={(quiz) => { setEditing(quiz); setView('editor'); }} onLaunch={launchQuiz} />}
      {user && view === 'editor' && <QuizEditorPage quiz={editing} onCancel={() => setView('quizzes')} onSave={saveQuiz} />}
      {user && view === 'room' && <OrganizerRoomPage room={room} onStart={() => api(`/rooms/${room.code}/start`, { method: 'POST' }).catch((err) => setError(err.message))} />}
      {user && view === 'play' && (
        <PlayRoomPage
          room={room}
          user={user}
          onAnswer={async (answerIds) => {
            const data = await api(`/rooms/${room.code}/answer`, { method: 'POST', body: { userId: user.id, answerIds } });
            setRoom(data.room);
            return data;
          }}
        />
      )}
      {user && view === 'history' && <HistoryPage history={history} user={user} />}
    </Layout>
  );
}
