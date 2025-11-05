import { useState, useEffect } from 'react';


function useSystemDarkMode() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check if window.matchMedia is available (browser environment)
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

      // Set initial state
      setIsDarkMode(mediaQuery.matches);

      // Listen for changes
      const handleChange = (e: any) => {
        setIsDarkMode(e.matches);
      };
      mediaQuery.addEventListener('change', handleChange);

      // Clean up the event listener on unmount
      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, []); // Empty dependency array ensures this runs only once on mount

  return isDarkMode;
}

export default useSystemDarkMode;