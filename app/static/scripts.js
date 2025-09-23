window.onload = function() {
    // modifique a escala para 80%
    document.body.style.zoom = "90%";
}

    // Function to create and show custom alert with animation
    function showCustomAlert(message) {
        // Remove existing alert if any
        if (document.getElementById("custom-alert")) {
            document.getElementById("custom-alert").remove();
        }

        // Create the alert HTML structure
        let alertHTML = `
            <div id="custom-alert" class="custom-alert-modal">
                <div class="custom-alert-content">
                    <span class="close-alert">&times;</span>
                    <p id="alert-message">${message}</p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', alertHTML);

        // Add CSS dynamically
        const styles = `
            /* Custom Alert Modal Style */
            .custom-alert-modal {
                display: none; /* Hidden by default */
                position: fixed;
                z-index: 1000; /* On top of other elements */
                left: 50%; /* Center horizontally */
                width: auto;
                height: auto;
                /*background-color: rgba(0, 0, 0, 0.4);  Black background with opacity */
                justify-content: center;
                align-items: center;
                animation: fadeIn 0.5s ease; /* Fade-in animation */
            }

            .custom-alert-content {
                background-color:#fff;
                border-radius: 10px;
                padding: 10px;
                width: 300px;
                text-align: center;
                animation: slideIn 0.5s ease forwards; /* Slide-in animation */

                position: relative;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }

            /* Close button style */
            .close-alert {
                position: absolute;
                top: 10px;
                right: 15px;
                font-size: 20px;
                cursor: pointer;
            }

            /* Slide-in from the top */
            @keyframes slideIn {
                from {
                    transform: translate(-50%, -100%); /* Start above the screen */
                }
                to {
                    transform: translate(-50%, 0); /* End in the centered top */
                }
            }

            /* Slide-out to the top */
            @keyframes slideOut {
                from {
                    transform: translate(-50%, 0); /* Start from the top center */
                }
                to {
                    transform: translate(-50%, -100%); /* Move back outside the screen */
                }
            }

        `;
        const styleSheet = document.createElement("style");
        styleSheet.type = "text/css";
        styleSheet.innerText = styles;
        document.head.appendChild(styleSheet);

        // Show the alert modal
        let alertModal = document.getElementById("custom-alert");
        alertModal.style.display = "flex";

        // Add close functionality
        document.querySelector(".close-alert").addEventListener("click", closeCustomAlert);

        // Close the modal when the 'X' is clicked
        $(".close-alert").click(() => {
            closeCustomAlert();
        });
    }

    // Function to close the custom alert
    function closeCustomAlert() {
        let alertContent = document.querySelector(".custom-alert-content");
        alertContent.style.animation = "slideOut 0.5s ease forwards";
        setTimeout(() => {
            let alertModal = document.getElementById("custom-alert");
            if (alertModal) alertModal.remove();
        }, 100); // Wait for the animation to finish
    }
