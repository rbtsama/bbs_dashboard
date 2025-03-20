const Header = ({ isScrolled }) => {
  return (
    <header 
      className={`site-header ${isScrolled ? 'scrolled' : ''}`}
      data-scrolled={isScrolled}
    >
      {/* ... existing code ... */}
    </header>
  );
};

// ... existing code ... 