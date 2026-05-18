const fallbackImage = "/static/images/product-placeholder.svg";

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
        const [key, value] = cookie.trim().split("=");
        if (key === name) {
            return decodeURIComponent(value);
        }
    }
    return "";
}

function showToast(message, type = "success") {
    const area = document.getElementById("toast-area");
    if (!area || !window.bootstrap) {
        alert(message);
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute("role", "status");
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
        </div>
    `;
    area.appendChild(toast);
    const instance = new bootstrap.Toast(toast, { delay: 3000 });
    instance.show();
    toast.addEventListener("hidden.bs.toast", () => toast.remove());
}

function productCard(product) {
    const image = product.image_url || product.product_image || fallbackImage;
    const stock = Number(product.stock_quantity);
    const button = stock > 0
        ? `<button class="btn btn-primary js-add-to-cart" type="button" data-product-id="${product.id}">В корзину</button>`
        : `<button class="btn btn-secondary" type="button" disabled>Нет</button>`;

    return `
        <div class="col-sm-6 col-lg-4">
            <article class="card product-card h-100">
                <img src="${image}" class="card-img-top" alt="${product.name}" onerror="this.src='${fallbackImage}'">
                <div class="card-body d-flex flex-column">
                    <p class="small text-muted mb-1">${product.category_name || ""}${product.manufacturer_name ? " · " + product.manufacturer_name : ""}</p>
                    <h3 class="h6 card-title">${product.name}</h3>
                    <p class="fw-bold price mb-3">${product.price} BYN</p>
                    <div class="mt-auto d-flex gap-2">
                        <a class="btn btn-outline-dark flex-fill" href="/catalog/${product.id}/">Подробнее</a>
                        ${button}
                    </div>
                </div>
            </article>
        </div>
    `;
}

async function loadCatalogProducts() {
    const list = document.getElementById("product-list");
    if (!list?.dataset.apiCatalog) {
        return;
    }

    const spinner = document.getElementById("catalog-spinner");
    const errorBox = document.getElementById("catalog-error");
    const params = new URLSearchParams(window.location.search);
    params.delete("page");

    spinner?.classList.remove("d-none");
    errorBox?.classList.add("d-none");

    try {
        const response = await fetch(`/api/products/?${params.toString()}`);
        if (!response.ok) {
            throw new Error("API вернул ошибку");
        }
        const data = await response.json();
        const products = Array.isArray(data) ? data : data.results;
        list.innerHTML = products.length
            ? products.map(productCard).join("")
            : `<div class="col-12"><div class="alert alert-info">По выбранным фильтрам товары не найдены.</div></div>`;
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = "Не удалось загрузить товары из API. Показана серверная версия каталога.";
            errorBox.classList.remove("d-none");
        }
    } finally {
        spinner?.classList.add("d-none");
    }
}

async function addToCart(productId) {
    const response = await fetch("/api/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Не удалось добавить товар.");
    }

    return data;
}

document.addEventListener("click", async (event) => {
    const button = event.target.closest(".js-add-to-cart");
    if (!button) {
        return;
    }

    button.disabled = true;
    try {
        const data = await addToCart(button.dataset.productId);
        showToast(data.detail || "Товар добавлен в корзину.");
    } catch (error) {
        showToast(error.message, "danger");
    } finally {
        button.disabled = false;
    }
});

document.addEventListener("DOMContentLoaded", loadCatalogProducts);
