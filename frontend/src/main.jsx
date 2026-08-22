import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Link,
  NavLink,
  Route,
  Routes,
  useParams,
} from "react-router-dom";
import { createClient } from "@supabase/supabase-js";
import "./styles.css";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);
const colors = ["#e07a5f", "#2d6a8f", "#d9b44a", "#815ac0"];
function Icon({ name, size = 18 }) {
  const p = {
    search: (
      <>
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4 4" />
      </>
    ),
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    sun: <circle cx="12" cy="12" r="4" />,
    moon: <path d="M20 15.2A8.5 8.5 0 0 1 8.8 4 8.5 8.5 0 1 0 20 15.2Z" />,
    chevron: <path d="m8 10 4 4 4-4" />,
    back: <path d="m15 18-6-6 6-6" />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {p[name]}
    </svg>
  );
}
function time(date) {
  if (!date) return "Recently";
  const h = Math.max(0, Math.floor((Date.now() - new Date(date)) / 36e5));
  return h < 1 ? "Just now" : `${h}h ago`;
}
function Header({ theme, onThemeToggle }) {
  return (
    <header>
      <div className="topbar">
        <Link className="brand" to="/">
          bias<span>scope</span>
          <b>•</b>
        </Link>
        <nav>
          <NavLink end to="/">
            Top Stories
          </NavLink>
          <NavLink to="/rising">Rising Stories</NavLink>
        </nav>
        <div className="actions">
        <button className="icon-btn theme-toggle" onClick={onThemeToggle} aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}>
          <Icon name={theme === "light" ? "moon" : "sun"} />
          </button>
          <button className="profile">JS</button>
        </div>
      </div>
    </header>
  );
}
function Mosaic({ large, image, title }) {
  return (
    <div className={`mosaic ${large ? "large" : ""}`}>
      {image ? (
        <img src={image} alt={title ? `Illustration for ${title}` : "Event illustration"} />
      ) : (
        colors.map((color, i) => <div key={i} style={{ background: color }} />)
      )}
    </div>
  );
}
function EventCard({ event, featured, wide }) {
  const count = event.articles?.[0]?.count || 0;
  return (
    <Link
      className={`event-card ${featured ? "featured" : ""} ${wide ? "wide" : ""}`}
      to={`/event/${event.id}`}
    >
      <Mosaic large={featured || wide} image={event.image} title={event.title} />
      <div className="card-content">
        <h2>{event.title || "Untitled event"}</h2>
        {(featured || wide) && (
          <p>
            {event.summary ||
              "Follow this developing story and read coverage from all linked sources."}
          </p>
        )}
        <div className="card-footer">
          <div className="article-count">
            <strong>{count}</strong> articles
          </div>
        </div>
      </div>
      
    </Link>
  );
}
function EventFeed({ rising = false, theme, onThemeToggle }) {
  const [events, setEvents] = useState([]),
    [query, setQuery] = useState(""),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  useEffect(() => {
    (async () => {
      const { data, error } = await supabase
        .from("events")
        .select("id,title,summary,image,created_at,articles(count)")
        .order("created_at", { ascending: false });
      if (error) setError(error.message);
      else
        setEvents(
          (data || []).sort(
            (a, b) =>
              (b.articles?.[0]?.count || 0) - (a.articles?.[0]?.count || 0),
          ),
        );
      setLoading(false);
    })();
  }, []);
  const subset = rising ? events.slice(20) : events.slice(0, 20);
  const filtered = useMemo(
    () =>
      subset.filter((e) =>
        (e.title || "").toLowerCase().includes(query.toLowerCase()),
      ),
    [subset, query],
  );
  return (
    <>
    <Header theme={theme} onThemeToggle={onThemeToggle} />
      <main>
        <section className="intro">
          <div>
            <div className="kicker">
              <span /> LIVE NEWS INTELLIGENCE
            </div>
            <h1>
              {rising ? (
                <>
                  Stories <em>on the rise.</em>
                </>
              ) : (
                <>
                  See the story
                  <br />
                  <em>behind the story.</em>
                </>
              )}
            </h1>
            <p>
              {rising
                ? "Events gaining attention across the news, organized by their connected coverage."
                : "Major events, organized from every angle. Follow what matters and understand how it’s being covered."}
            </p>
          </div>
          <div className="date-block">
            <span>
              {new Date()
                .toLocaleDateString(undefined, { weekday: "long" })
                .toUpperCase()}
            </span>
            <strong>{new Date().getDate()}</strong>
            <small>
              {new Date()
                .toLocaleDateString(undefined, {
                  month: "long",
                  year: "numeric",
                })
                .toUpperCase()}
            </small>
          </div>
        </section>
        <section className="toolbar">
          <div className="section-title">
            {rising ? "Rising stories" : "Today’s events"}{" "}
            <small>{filtered.length} stories</small>
          </div>
          <div className="filters">
            <label className="search-box">
              <Icon name="search" size={16} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search events"
              />
            </label>
          </div>
        </section>
        {loading ? (
          <div className="empty">Loading events…</div>
        ) : error ? (
          <div className="empty">Couldn’t load events: {error}</div>
        ) : filtered.length ? (
          <section className="event-grid">
            {filtered.map((e, i) => (
              <EventCard
                event={e}
                featured={!rising && i === 0}
                wide={i > 3 && [5, 11, 17].includes(i)}
                key={e.id}
              />
            ))}
          </section>
        ) : (
          <div className="empty">No events match your search.</div>
        )}
      </main>
    </>
  );
}
function EventPage({ theme, onThemeToggle }) {
  const { eventid } = useParams();
  const [event, setEvent] = useState(),
    [articles, setArticles] = useState([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  useEffect(() => {
    (async () => {
      const [er, ar] = await Promise.all([
        supabase
          .from("events")
          .select("id,title,summary,created_at")
          .eq("id", eventid)
          .single(),
        supabase
          .from("articles")
          .select("id,title,description,author,published_at,source,url")
          .eq("cluster", eventid)
          .order("published_at", { ascending: false }),
      ]);
      if (er.error) setError(er.error.message);
      else {
        setEvent(er.data);
        setArticles(ar.data || []);
        if (ar.error) setError(ar.error.message);
      }
      setLoading(false);
    })();
  }, [eventid]);
  return (
    <>
    <Header theme={theme} onThemeToggle={onThemeToggle} />
      <main className="event-page">
        {loading ? (
          <div className="empty">Loading event coverage…</div>
        ) : error ? (
          <div className="empty">Couldn’t load this event: {error}</div>
        ) : (
          <>
            <Link className="back-link" to="/">
              <Icon name="back" size={16} /> All events
            </Link>
            <section className="event-hero">
              <div className="eyebrow">
                DEVELOPING EVENT · {time(event.created_at)}
              </div>
              <h1>{event.title || "Untitled event"}</h1>
              {event.summary && <p>{event.summary}</p>}
              <div className="event-total">
                <strong>{articles.length}</strong>
                <span>
                  linked articles
                  <br />
                  in this event
                </span>
              </div>
            </section>
            <section className="coverage-header">
              <h2>Coverage</h2>
              <span>{articles.length} articles, newest first</span>
            </section>
            <section className="article-list">
              {articles.length ? (
                articles.map((a) => (
                  <a
                    className="article-row"
                    key={a.id}
                    href={a.url || "#"}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <div className="article-mark">
                      {(a.source || "N")[0].toUpperCase()}
                    </div>
                    <div>
                      <div className="article-meta">
                        {a.source || "Unknown source"}
                        <i /> {time(a.published_at)}
                      </div>
                      <h3>{a.title}</h3>
                      {a.description && <p>{a.description}</p>}
                      <small>{a.author && `By ${a.author}`}</small>
                    </div>
                    <Icon name="arrow" />
                  </a>
                ))
              ) : (
                <div className="empty">
                  No articles have been linked to this event yet.
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </>
  );
}
function App() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const toggleTheme = () => setTheme((current) => (current === "light" ? "dark" : "light"));

  return (
    <Routes>
      <Route path="/" element={<EventFeed theme={theme} onThemeToggle={toggleTheme} />} />
      <Route path="/rising" element={<EventFeed rising theme={theme} onThemeToggle={toggleTheme} />} />
      <Route path="/event/:eventid" element={<EventPage theme={theme} onThemeToggle={toggleTheme} />} />
    </Routes>
  );
}
createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
