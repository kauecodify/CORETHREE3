import React from 'react';
import Head from 'next/head';
import '../styles/global.css';
import '../styles/rainbow.css';

const Layout = ({ children, title = 'CORETHREE3 - Plataforma de Solucoes Integradas' }) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Plataforma TRL 8 para automacao industrial, varejo inteligente e logistica com IA/ML e sensores IoT" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#2563eb" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code&display=swap" rel="stylesheet" />
      </Head>
      
      <div className="core-three-layout">
        {/* Rainbow Background */}
        <div className="rainbow-wave-container">
          <div className="rainbow-wave-item"></div>
          <div className="rainbow-wave-item"></div>
          <div className="rainbow-wave-item"></div>
          <div className="rainbow-wave-item"></div>
        </div>
        
        {/* Main Content */}
        <div className="core-three-content">
          {children}
        </div>
        
        {/* Watermark */}
        <div className="core-three-watermark">
          <div className="core-three-watermark-symbol">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#6b7280" />
            </svg>
          </div>
          <div className="core-three-watermark-text">
            <span className="core-three-watermark-text-primary">hacka corethree</span>
            <span className="core-three-watermark-text-secondary">by laboratory of k</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Layout;
