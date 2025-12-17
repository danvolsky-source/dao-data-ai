'use client';

import React from 'react';

const Header = () => {
  return (
    <header className="glass sticky top-0 z-50 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold gradient-text">
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
            <a
              href="mailto:info@sky-mind.com"
              className="btn btn-primary"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
