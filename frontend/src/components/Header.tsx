import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => (
  <header className="header">
    <nav>
      <ul>
        <li>
          <Link to="/">Walls</Link>
        </li>
        <li>
          <Link to="/walls/new">Create Wall</Link>
        </li>
      </ul>
    </nav>
  </header>
);

export default Header;