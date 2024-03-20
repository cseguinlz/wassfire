document.addEventListener("DOMContentLoaded", function () {
    // Function to handle opening of a specific flyout menu
    const openFlyoutMenu = (menuId) => {
      const menu = document.getElementById(menuId);
      menu.classList.remove("hidden"); // Show the menu
      const buttonId = menu.getAttribute("data-related-button");
      const button = document.getElementById(buttonId);
      button.setAttribute("aria-expanded", "true");
    };
  
    // Function to handle closing of a specific flyout menu
    const closeFlyoutMenu = (menuId) => {
      const menu = document.getElementById(menuId);
      menu.classList.add("hidden"); // Hide the menu
      const buttonId = menu.getAttribute("data-related-button");
      const button = document.getElementById(buttonId);
      button.setAttribute("aria-expanded", "false");
    };
  
    // Event listeners for menu buttons
    document.querySelectorAll(".menuButton").forEach((button) => {
      const menuId = button.getAttribute("aria-controls");
      const menu = document.getElementById(menuId);
  
      // Open flyout menu on mouse over
      button.addEventListener("mouseover", () => openFlyoutMenu(menuId));
  
      // Close flyout menu on mouse leave from the button and menu itself
      menu.addEventListener("mouseleave", () => closeFlyoutMenu(menuId));
      button.addEventListener("mouseleave", (event) => {
        // Check if the mouse is moving towards the menu; if not, close the menu
        if (!menu.contains(event.relatedTarget)) {
          closeFlyoutMenu(menuId);
        }
      });
    });
  
    // Keep the functionality to close menus when clicking outside or pressing Escape
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".menuButton, .flyoutMenu")) {
        document.querySelectorAll(".flyoutMenu").forEach((menu) => {
          menu.classList.add("hidden");
          const relatedButtonId = menu.getAttribute("data-related-button");
          const relatedButton = document.getElementById(relatedButtonId);
          if (relatedButton) {
            relatedButton.setAttribute("aria-expanded", "false");
          }
        });
      }
    });
  
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        document.querySelectorAll(".flyoutMenu").forEach((menu) => {
          menu.classList.add("hidden");
          const relatedButtonId = menu.getAttribute("data-related-button");
          const relatedButton = document.getElementById(relatedButtonId);
          if (relatedButton) {
            relatedButton.setAttribute("aria-expanded", "false");
          }
        });
      }
    });
  });
  

document.addEventListener('DOMContentLoaded', function () {
    const menuToggleButton = document.getElementById('menuToggle');
    const closeButton = document.querySelector('#mobileMenu button'); // Ensure this selector targets the close button correctly
    const mobileMenu = document.getElementById('mobileMenu');
  
    // Function to toggle the visibility of the mobile menu
    function toggleMenu() {
      mobileMenu.classList.toggle('hidden');
    }
  
    // Event listeners for the toggle and close buttons
    menuToggleButton.addEventListener('click', toggleMenu);
    closeButton.addEventListener('click', toggleMenu);
  });
  