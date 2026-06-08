/* ============================================
   INVENTORY PAGE JS
   ============================================ */

// Sample product catalog
const allProducts = [
  { name: '6 pack Bananas', category: 'fresh' },
  { name: '1Kg Apples', category: 'fresh' },
  { name: '500g Strawberries', category: 'fresh' },
  { name: '1L Milk', category: 'refrigerated' },
  { name: '2L Soy Milk', category: 'refrigerated' },
  { name: '2L Orange Juice', category: 'drink' },
  { name: '1L Apple Juice', category: 'drink' },
  { name: '400g Canned Beans', category: 'canned' },
  { name: '200g Canned Corn', category: 'canned' },
].sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));

// Inventory data
let inventory = [
  { id: 1, productName: '6 pack Bananas', category: 'fresh', quantity: 30, expiryDate: '2026-06-03', daysLeft: 2 },
  { id: 2, productName: '1Kg Apples', category: 'fresh', quantity: 50, expiryDate: '2026-06-05', daysLeft: 4 },
  { id: 3, productName: '1L Milk', category: 'refrigerated', quantity: 24, expiryDate: '2026-06-07', daysLeft: 6 },
  { id: 4, productName: '2L Orange Juice', category: 'drink', quantity: 36, expiryDate: '2026-06-10', daysLeft: 9 },
  { id: 5, productName: '400g Canned Beans', category: 'canned', quantity: 120, expiryDate: '2027-03-15', daysLeft: 274 },
  { id: 6, productName: '6 pack Bananas', category: 'fresh', quantity: 20, expiryDate: '2026-06-08', daysLeft: 7 },
  { id: 7, productName: '1Kg Apples', category: 'fresh', quantity: 35, expiryDate: '2026-06-12', daysLeft: 11 },
  { id: 8, productName: '1L Milk', category: 'refrigerated', quantity: 18, expiryDate: '2026-06-04', daysLeft: 3 },
  { id: 9, productName: '2L Orange Juice', category: 'drink', quantity: 42, expiryDate: '2026-06-15', daysLeft: 14 },
  { id: 10, productName: '400g Canned Beans', category: 'canned', quantity: 80, expiryDate: '2027-04-20', daysLeft: 305 },
];

// State
let sortField = null;
let sortDirection = 'asc';
let productFilter = '';
let categoryFilter = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  // Set min date for expiry date input to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('formExpiryDate').min = today;
  
  populateProductDropdown();
  renderInventoryTable();
  updateActiveFilters();
  
  // Event listeners
  document.getElementById('addDonationForm').addEventListener('submit', handleAddDonation);
  document.getElementById('filterProduct').addEventListener('input', function(e) {
    productFilter = e.target.value;
    renderInventoryTable();
    updateActiveFilters();
  });
  document.getElementById('filterCategory').addEventListener('change', function(e) {
    categoryFilter = e.target.value;
    renderInventoryTable();
    updateActiveFilters();
  });
});

// Populate product dropdown
function populateProductDropdown() {
  const menu = document.getElementById('productDropdownMenu');
  let currentCategory = '';
  
  let html = '';
  allProducts.forEach(product => {
    if (product.category !== currentCategory) {
      currentCategory = product.category;
      html += `<li><span class="dropdown-item-category text-capitalize">${currentCategory}</span></li>`;
    }
    html += `<li><a class="dropdown-item-product" href="#" onclick="selectProduct('${product.name}', '${product.category}'); return false;">${product.name}</a></li>`;
  });
  
  menu.innerHTML = html;
}

// Select product from dropdown
function selectProduct(name, category) {
  document.getElementById('selectedProductText').textContent = name;
  document.getElementById('formProductName').value = name;
  document.getElementById('formCategory').value = category;
}

// Get category badge class
function getCategoryBadgeClass(category) {
  const classes = {
    fresh: 'badge-fresh',
    refrigerated: 'badge-refrigerated',
    drink: 'badge-drink',
    canned: 'badge-canned'
  };
  return classes[category] || 'badge-fresh';
}

// Get status badge
function getStatusBadge(daysLeft) {
  if (daysLeft <= 2) {
    return `<span class="badge-status status-critical"><i class="bi bi-exclamation-triangle-fill"></i> ${daysLeft}d left</span>`;
  } else if (daysLeft <= 6) {
    return `<span class="badge-status status-warning"><i class="bi bi-clock-fill"></i> ${daysLeft}d left</span>`;
  } else {
    return `<span class="badge-status status-good"><i class="bi bi-check-circle-fill"></i> ${daysLeft}d left</span>`;
  }
}

// Format date for display
function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Handle sort
function handleSort(field) {
  if (sortField === field) {
    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
  } else {
    sortField = field;
    sortDirection = 'asc';
  }
  
  // Update sort icons
  document.querySelectorAll('.sort-icon').forEach(icon => {
    icon.className = 'bi bi-chevron-expand sort-icon';
  });
  const activeIcon = document.getElementById(`sort-${field}`);
  if (activeIcon) {
    activeIcon.className = `bi bi-chevron-${sortDirection === 'asc' ? 'up' : 'down'} sort-icon text-golden`;
  }
  
  renderInventoryTable();
}

// Filter inventory
function getFilteredInventory() {
  return inventory.filter(item => {
    const matchesProduct = productFilter === '' || item.productName.toLowerCase().includes(productFilter.toLowerCase());
    const matchesCategory = categoryFilter === '' || item.category === categoryFilter;
    return matchesProduct && matchesCategory;
  });
}

// Sort inventory
function getSortedInventory(filtered) {
  if (!sortField) return filtered;
  
  return [...filtered].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    const direction = sortDirection === 'asc' ? 1 : -1;
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return aValue.localeCompare(bValue) * direction;
    }
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return (aValue - bValue) * direction;
    }
    return 0;
  });
}

// Render inventory table
function renderInventoryTable() {
  const tbody = document.getElementById('inventoryTableBody');
  const emptyState = document.getElementById('emptyState');
  
  const filtered = getFilteredInventory();
  const sorted = getSortedInventory(filtered);
  
  if (sorted.length === 0) {
    tbody.innerHTML = '';
    emptyState.classList.remove('d-none');
    return;
  }
  
  emptyState.classList.add('d-none');
  
  tbody.innerHTML = sorted.map(item => `
    <tr>
      <td>${item.productName}</td>
      <td><span class="badge-category ${getCategoryBadgeClass(item.category)} text-capitalize">${item.category}</span></td>
      <td>${formatDate(item.expiryDate)}</td>
      <td>${getStatusBadge(item.daysLeft)}</td>
      <td>
        <div class="quantity-control">
          <button class="btn-quantity btn-decrement" onclick="decrementQuantity(${item.id})">
            <i class="bi bi-dash"></i>
          </button>
          <input type="number" class="quantity-input" value="${item.quantity}" 
                 onchange="updateQuantity(${item.id}, this.value)" min="0">
          <button class="btn-quantity btn-increment" onclick="incrementQuantity(${item.id})">
            <i class="bi bi-plus"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

// Update active filters display
function updateActiveFilters() {
  const container = document.getElementById('activeFilters');
  
  if (!productFilter && !categoryFilter) {
    container.innerHTML = '';
    return;
  }
  
  let html = '<span class="me-2 text-muted small">Active filters:</span>';
  
  if (categoryFilter) {
    html += `
      <span class="filter-badge me-2">
        Category: ${categoryFilter}
        <button onclick="clearCategoryFilter()"><i class="bi bi-x"></i></button>
      </span>
    `;
  }
  
  if (productFilter) {
    html += `
      <span class="filter-badge me-2">
        Product: ${productFilter}
        <button onclick="clearProductFilter()"><i class="bi bi-x"></i></button>
      </span>
    `;
  }
  
  html += `<button class="btn-clear-filters" onclick="clearAllFilters()">Clear all</button>`;
  container.innerHTML = html;
}

function clearCategoryFilter() {
  categoryFilter = '';
  document.getElementById('filterCategory').value = '';
  renderInventoryTable();
  updateActiveFilters();
}

function clearProductFilter() {
  productFilter = '';
  document.getElementById('filterProduct').value = '';
  renderInventoryTable();
  updateActiveFilters();
}

function clearAllFilters() {
  productFilter = '';
  categoryFilter = '';
  document.getElementById('filterProduct').value = '';
  document.getElementById('filterCategory').value = '';
  renderInventoryTable();
  updateActiveFilters();
}

// Quantity handlers
function incrementQuantity(id) {
  const item = inventory.find(i => i.id === id);
  if (item) {
    item.quantity++;
    renderInventoryTable();
  }
}

function decrementQuantity(id) {
  const item = inventory.find(i => i.id === id);
  if (item && item.quantity > 0) {
    item.quantity--;
    renderInventoryTable();
  }
}

function updateQuantity(id, value) {
  const item = inventory.find(i => i.id === id);
  if (item) {
    item.quantity = parseInt(value) || 0;
    renderInventoryTable();
  }
}

// Add donation
function handleAddDonation(e) {
  e.preventDefault();
  
  const productName = document.getElementById('formProductName').value;
  const category = document.getElementById('formCategory').value;
  const quantity = parseInt(document.getElementById('formQuantity').value) || 0;
  const expiryDate = document.getElementById('formExpiryDate').value;
  
  if (!productName || !category || !quantity || !expiryDate) {
    showToast('Please fill in all fields.');
    return;
  }
  
  const expiry = new Date(expiryDate + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
  
  const newItem = {
    id: Date.now(),
    productName,
    category,
    quantity,
    expiryDate,
    daysLeft
  };
  
  inventory.push(newItem);
  
  // Reset form
  document.getElementById('addDonationForm').reset();
  document.getElementById('selectedProductText').textContent = 'Select product';
  document.getElementById('formProductName').value = '';
  
  // Default sort by expiry date to show new item in correct place
  sortField = 'expiryDate';
  sortDirection = 'asc';
  
  renderInventoryTable();
  showToast(`${productName} added to inventory!`);
}

// Submit updates
function submitUpdates() {
  const message = document.getElementById('updateMessage');
  message.classList.remove('d-none');
  setTimeout(() => {
    message.classList.add('d-none');
  }, 3000);
  showToast('Inventory updates saved successfully!');
}