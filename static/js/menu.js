
    // Open Modals
    document.querySelector("#addCategoryBtn").addEventListener("click", () => {
        document.getElementById("categoryModal").style.display = "flex";
        document.getElementById("categoryForm").reset();
        document.getElementById("modalTitle").innerText = "Add Category";
    });


    document.querySelectorAll(".add-menu-item").forEach(btn => {
        btn.addEventListener("click", () => {
            const categoryId = btn.closest(".dropdown-content").id.split("-")[1];
            const dropdown = document.getElementById(`dropdown-${categoryId}`);
            const isDropdownOpen = dropdown.getAttribute("data-open") === "true";
            
            if (isDropdownOpen) {
                // Save the open dropdown state
                sessionStorage.setItem("openDropdown", categoryId);
            }
            document.getElementById("menuItemModal").style.display = "flex";
            document.getElementById("menuItemForm").reset();
            document.getElementById("menuItemModalTitle").innerText = "Add Menu Item";
            document.getElementById("menuItemCategoryId").value = btn.dataset.categoryId;
        });
    });

    document.querySelectorAll(".edit-category").forEach(btn => {
        btn.addEventListener("click", () => {
            document.getElementById("categoryModal").style.display = "flex";
            document.getElementById("modalTitle").innerText = "Edit Category";

            const categoryId = btn.dataset.id;
            fetch(`/admin/category/${categoryId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById("categoryId").value = data.id;
                    document.getElementById("categoryName").value = data.name;
                    document.getElementById("categoryDescription").value = data.description;
                });
        });
    });

    document.querySelectorAll(".close-modal").forEach(btn => {
    btn.addEventListener("click", () => {
        btn.parentElement.style.display = "none";
        document.getElementById("menuItemImagePreview").src = "";
    });
});

document.querySelectorAll(".edit-item").forEach(btn => {
    btn.addEventListener("click", () => {
        const itemId = btn.dataset.id;
        const categoryId = btn.closest(".dropdown-content").id.split("-")[1]
        const dropdown = document.getElementById(`dropdown-${categoryId}`);
        const isDropdownOpen = dropdown.getAttribute("data-open") === "true";
        
        if (isDropdownOpen) {
            // Save the open dropdown state
            sessionStorage.setItem("openDropdown", categoryId);
        }
        // Reset modal and show it
        document.getElementById("menuItemModal").style.display = "flex";
        document.getElementById("menuItemForm").reset();
        document.getElementById("menuItemModalTitle").innerText = "Edit Menu Item";

        // Fetch the menu item details
        fetch(`/admin/menu_item/${itemId}`)
            .then(res => res.json())
            .then(data => {
                // Populate fields with fetched data
                document.getElementById("menuItemId").value = data.id;
                document.getElementById("menuItemName").value = data.name;
                document.getElementById("menuItemPrice").value = data.price;
                document.getElementById("menuItemDiscountedPrice").value = data.discountedPrice;
                document.getElementById("menuItemPreparationTime").value = data.preparation_time;

                // Handle the image preview
                const preview = document.getElementById("menuItemImagePreview");
                const placeholder = document.querySelector(".upload-placeholder");
                if (data.image_url) {
                    preview.src = data.image_url; // Set the current image URL
                    preview.style.display = "block"; // Show the image
                    placeholder.style.display = "none"; // Hide the placeholder
                } else {
                    preview.src = "";
                    preview.style.display = "none"; // Hide the image
                    placeholder.style.display = "flex"; // Show the placeholder
                }
            })
            .catch(err => {
                console.error("Error fetching item details:", err);
                alert("Failed to load item details.");
            });
    });
});

    document.getElementById("categoryForm").addEventListener("submit", e => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const action = formData.get("category_id") ? `/admin/category/edit/${formData.get("category_id")}` : "/admin/category/add";

    fetch(action, { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.message.includes("successfully")) {
                location.reload();
            }
        })
        .catch(err => {
            console.error(err);
            alert("An error occurred while saving the category.");
        });
});

document.getElementById("menuItemForm").addEventListener("submit", e => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const action = formData.get("item_id")
        ? `/admin/menu_item/edit/${formData.get("item_id")}`
        : "/admin/menu_item/add";

    fetch(action, { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(err => {
            console.error("Error:", err);
            alert("An error occurred while saving the menu item.");
        });
});

    // Delete Actions
    document.querySelectorAll(".delete-category").forEach(btn => {
        btn.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete this category?")) {
                fetch(`/admin/category/delete/${btn.dataset.id}`, { method: "POST" })
                    .then(res => res.json())
                    .then(data => {
                        alert(data.message);
                        location.reload();
                    });
            }
        });
    });

// Handle Delete Menu Item
document.querySelectorAll(".delete-item").forEach(btn => {
    btn.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete this menu item?")) {
            const categoryId = btn.closest(".dropdown-content").id.split("-")[1];
            const dropdown = document.getElementById(`dropdown-${categoryId}`);
            const isDropdownOpen = dropdown.getAttribute("data-open") === "true";

            fetch(`/admin/menu_item/delete/${btn.dataset.id}`, { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);

                    if (isDropdownOpen) {
                        // Save the open dropdown state
                        sessionStorage.setItem("openDropdown", categoryId);
                    }

                    location.reload(); // Reload the page to reflect changes
                })
                .catch(err => {
                    console.error("Error deleting menu item:", err);
                    alert("Failed to delete the menu item.");
                });
        }
    });
});

// Restore Open Dropdown on Page Load
document.addEventListener("DOMContentLoaded", () => {
    const openDropdownId = sessionStorage.getItem("openDropdown");
    if (openDropdownId) {
        const dropdown = document.getElementById(`dropdown-${openDropdownId}`);
        dropdown.style.display = "block";
        dropdown.setAttribute("data-open", "true");
    }

    // Clear session storage after restoring
    sessionStorage.removeItem("openDropdown");
});


    document.getElementById("menuItemImageInput").addEventListener("change", function (event) {
        const file = event.target.files[0];
        const preview = document.getElementById("menuItemImagePreview");
        const placeholder = document.querySelector(".upload-placeholder");
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                preview.style.display = "block"; // Show the image
                placeholder.style.display = "none"; // Hide the placeholder
            };
            reader.readAsDataURL(file);
        } else {
            preview.src = "";
            preview.style.display = "none"; // Hide the image
            placeholder.style.display = "flex"; // Show the placeholder
        }
    });
    
// Add event listeners to all category headers
document.querySelectorAll('.category-header').forEach(header => {
    header.addEventListener('click', function () {
        const id = this.getAttribute('data-id'); // Get the category ID
        const dropdown = document.getElementById(`dropdown-${id}`); // Target the dropdown
        const isOpen = dropdown.getAttribute('data-open') === 'true'; // Check open state

        // Toggle visibility
        if (isOpen) {
            dropdown.style.display = 'none'; // Hide
            dropdown.setAttribute('data-open', 'false'); // Update state
        } else {
            dropdown.style.display = 'block'; // Show
            dropdown.setAttribute('data-open', 'true'); // Update state
        }
    });
});