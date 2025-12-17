'use client';

import React from 'react';

const Header = () => {
  return (
    <header className="bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              🏛️ DAO Analytics
            </h1>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <a
              href="#dashboard"
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Dashboard
            </a>
            <a
              href="#proposals"
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Proposals
            </a>
            <a
              href="#analytics"
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Analytics
            </a>
            <a
              href="#alerts"
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Alerts
            </a>
          </nav>

          {/* CTA Button */}
          <div className="flex items-center space-x-4">
            <button className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:from-cyan-600 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl">
              Connect Wallet
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
