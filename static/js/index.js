document.addEventListener("DOMContentLoaded", function () {
    // Dropdown Toggle Logic
    const dropdownToggle = document.querySelector(".dropdown-toggle");
    const dropdownMenu = document.querySelector(".dropdown-menu");

    dropdownToggle.addEventListener("click", function (e) {
        e.preventDefault(); // Prevent the default link behavior
        dropdownMenu.classList.toggle("show"); // Toggle the "show" class
        this.classList.toggle("active"); // Toggle the arrow rotation
    });

    // Modal Logic
    const orderModal = document.getElementById("orderModal");
    const viewOrderBtn = document.getElementById("viewOrderBtn");
    const checkoutOrderBtn = document.getElementById("checkoutOrderBtn");
    const addItemsBtn = document.getElementById("addItemsBtn");
    const cancelOrderBtn = document.getElementById("cancelOrderBtn");

    // Function to show the modal
    function showModal() {
        orderModal.style.display = "flex";
    }

    // Function to hide the modal
    function hideModal() {
        orderModal.style.display = "none";
    }

    // Open modal when "View Order List" is clicked
    viewOrderBtn.addEventListener("click", function (e) {
        e.preventDefault();
        showModal();
    });

    // Open modal when "Check Out" is clicked
    checkoutOrderBtn.addEventListener("click", function (e) {
        e.preventDefault();
        showModal();
    });

    // Close modal when "Add More Items" is clicked
    addItemsBtn.addEventListener("click", function () {
        hideModal();
    });

    // Handle cancel order logic
    cancelOrderBtn.addEventListener("click", function () {
        fetch('/cancel_order', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear cart and update UI
                    document.getElementById('cartCounter').textContent = '0';
                    updateCartModal([], 0);
                }
            })
            .catch(error => console.error('Failed to cancel order:', error));

        hideModal();
    });

    // Add to cart button logic
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            const name = event.target.getAttribute('data-name');
            const price = parseFloat(event.target.getAttribute('data-price'));
            const imageUrl = event.target.getAttribute('data-image');
            const itemImageElement = event.target.closest('.cards').querySelector('img');

            // Animate the item to the cart
            animateAddToCart(itemImageElement);

            // Send data to the server
            fetch('/add_to_cart', {
                method: 'POST',
                body: new URLSearchParams({
                    name: name,
                    price: price.toFixed(2),
                    image_url: imageUrl
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Error:', data.error);
                    } else {
                        // Update cart modal and counter
                        updateCartModal(data.cart_items, data.total);
                        document.getElementById('cartCounter').textContent = data.cart_items.length;
                    }
                })
                .catch(error => {
                    console.error('Request failed', error);
                });
        });
    });

    // Fetch initial cart data on page load
    window.onload = function () {
        fetch('/cart_items')
            .then(response => response.json())
            .then(data => {
                document.getElementById('cartCounter').textContent = data.cart_items.length;
            })
            .catch(error => console.error('Failed to fetch cart data:', error));
    };
});
document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch cart items and update modal
    async function loadCartItems() {
        try {
            const response = await fetch('/cart_items');
            const data = await response.json();
            if (data.cart_items) {
                updateCartModal(data.cart_items, data.total);
            }
        } catch (error) {
            console.error('Failed to fetch cart items:', error);
        }
    }

    // Call loadCartItems when the page is ready
    loadCartItems();
})
// Update the cart modal with new data
function updateCartModal(cartItems, total) {
    // Ensure total is a number
    total = parseFloat(total);

    // Update cart total amount
    const totalAmountElement = document.querySelector('#totalAmount');
    if (totalAmountElement) {
        totalAmountElement.textContent = `₱${total.toFixed(2)}`;
    } else {
        console.error('Total amount element (#totalAmount) not found in the DOM.');
    }

    // Update cart items
    const orderItemsContainer = document.querySelector('#orderItems');
    if (orderItemsContainer) {
        orderItemsContainer.innerHTML = ''; // Clear existing items
        if (cartItems.length > 0) {
            cartItems.forEach(item => {
                const orderItemElement = document.createElement('div');
                orderItemElement.className = 'order-item';
                orderItemElement.innerHTML = `
                    <img src="${item.image_url}" alt="${item.name}" class="item-image">
                    <div class="item-details">
                        <p class="item-name">${item.name}</p>
                        <p class="item-price">₱${parseFloat(item.price).toFixed(2)}</p>
                    </div>
                    <div class="item-quantity">
                        <button class="minus-btn" data-id="${item.id}" data-action="decrement">-</button>
                        <input type="number" value="${item.quantity}" class="quantity-input" min="1" readonly>
                        <button class="plus-btn" data-id="${item.id}" data-action="increment">+</button>
                    </div>
                `;
                orderItemsContainer.appendChild(orderItemElement);
            });

            // Add event listeners to increment and decrement buttons
            document.querySelectorAll('.minus-btn, .plus-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const id = e.target.dataset.id;
                    const action = e.target.dataset.action;

                    if (!id || !action) {
                        console.error('Invalid button data: ID or action is missing.');
                        return;
                    }

                    try {
                        const response = await fetch(`/cart/update/${id}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ action }),
                        });

                        if (!response.ok) {
                            const error = await response.json();
                            alert(`Error: ${error.message || 'Failed to update cart.'}`);
                            return;
                        }
                        fetch('/cart_items')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('cartCounter').textContent = data.cart_items.length;
                            })
                            .catch(error => console.error('Failed to fetch cart data:', error));
                        const result = await response.json();

                        if (result.success) {
                            updateCartModal(result.cartItems, result.total);
                        } else {
                            alert(`Failed to update cart: ${result.message}`);
                        }
                    } catch (error) {
                        console.error('Error updating cart:', error);
                        alert('An error occurred while updating the cart.');
                    }
                });
            });
        }
    }
}

// Animation when adding an item to the cart
function animateAddToCart(itemImageElement) {
    const cartIcon = document.getElementById('cartIcon');
    if (!itemImageElement || !cartIcon) {
        console.error('Missing elements for animation:', { itemImageElement, cartIcon });
        return;
    }

    const cartRect = cartIcon.getBoundingClientRect();
    const itemRect = itemImageElement.getBoundingClientRect();

    // Create a clone of the item image for animation
    const clone = itemImageElement.cloneNode();
    clone.style.position = 'absolute';
    clone.style.top = `${itemRect.top}px`;
    clone.style.left = `${itemRect.left}px`;
    clone.style.width = `${itemRect.width}px`;
    clone.style.height = `${itemRect.height}px`;
    clone.style.transition = 'all 0.8s ease-in-out';
    clone.style.zIndex = '1000';
    document.body.appendChild(clone);

    // Animate to the cart
    setTimeout(() => {
        clone.style.top = `${cartRect.top}px`;
        clone.style.left = `${cartRect.left}px`;
        clone.style.width = '20px';
        clone.style.height = '20px';
        clone.style.opacity = '0.5';
    }, 0);

    // Remove the clone after animation
    setTimeout(() => {
        document.body.removeChild(clone);
    }, 800);
}

function sendCartToCheckout(event) {
    event.preventDefault();  // Prevents the default anchor navigation

    const cartItems = [...document.querySelectorAll('.order-item')].map(item => ({
        id: item.dataset.id,
        name: item.querySelector('.item-name').textContent,
        price: parseFloat(item.querySelector('.item-price').textContent.replace('₱', '')),
        quantity: parseInt(item.querySelector('.quantity-input').value),
        image_url: item.querySelector('img').src
    }));

    fetch('/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cart_items: cartItems })
    }).then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    });
}
