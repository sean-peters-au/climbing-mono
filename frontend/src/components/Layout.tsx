import React from 'react';
import './Layout.css';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => (
  <div className="layout">
    <Header />
    <main className="content">{children}</main>
  </div>
);

export default Layout;