const foodItemsByCategory = window.APP_DATA.foodItemsByCategory;
const wineTypesByCategory = window.APP_DATA.wineTypesByCategory;
const wineCategoriesByType = window.APP_DATA.wineCategoriesByType;

const allWineTypes = window.APP_DATA.allWineTypes;
const allWineCategories = window.APP_DATA.allWineCategories;
const allFoodItems = window.APP_DATA.allFoodItems;
const submittedValues = window.APP_DATA.submittedValues || {};

function updateSelectOptions(selectElement, options, selectedValue = "") {
    const currentValueStillValid = options.includes(selectedValue);

    selectElement.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select...";
    defaultOption.selected = !currentValueStillValid;
    selectElement.appendChild(defaultOption);

    options.forEach(optionValue => {
        const option = document.createElement("option");
        option.value = optionValue;
        option.textContent = optionValue;

        if (currentValueStillValid && optionValue === selectedValue) {
            option.selected = true;
        }

        selectElement.appendChild(option);
    });
}

function updateFoodItems() {
    const foodCategorySelect = document.getElementById("food_category");
    const foodItemSelect = document.getElementById("food_item");

    const selectedCategory = foodCategorySelect.value;
    const currentFoodItem = foodItemSelect.value || submittedValues.food_item || "";

    const validFoodItems = selectedCategory
        ? (foodItemsByCategory[selectedCategory] || [])
        : allFoodItems;

    updateSelectOptions(foodItemSelect, validFoodItems, currentFoodItem);
}

function updateWineFields() {
    const wineTypeSelect = document.getElementById("wine_type");
    const wineCategorySelect = document.getElementById("wine_category");

    let selectedWineType = wineTypeSelect.value || submittedValues.wine_type || "";
    let selectedWineCategory = wineCategorySelect.value || submittedValues.wine_category || "";

    let validWineTypes = allWineTypes;
    let validWineCategories = allWineCategories;

    if (selectedWineCategory) {
        validWineTypes = wineTypesByCategory[selectedWineCategory] || [];
    }

    if (selectedWineType) {
        validWineCategories = wineCategoriesByType[selectedWineType] || [];
    }

    if (selectedWineCategory && selectedWineType) {
        const typesFromCategory = new Set(wineTypesByCategory[selectedWineCategory] || []);
        const categoriesFromType = new Set(wineCategoriesByType[selectedWineType] || []);

        if (!typesFromCategory.has(selectedWineType)) {
            selectedWineType = "";
        }

        if (!categoriesFromType.has(selectedWineCategory)) {
            selectedWineCategory = "";
        }

        validWineTypes = selectedWineCategory
            ? (wineTypesByCategory[selectedWineCategory] || [])
            : allWineTypes;

        validWineCategories = selectedWineType
            ? (wineCategoriesByType[selectedWineType] || [])
            : allWineCategories;
    }

    updateSelectOptions(wineTypeSelect, validWineTypes, selectedWineType);
    updateSelectOptions(wineCategorySelect, validWineCategories, selectedWineCategory);
}

document.addEventListener("DOMContentLoaded", function () {
    const foodCategorySelect = document.getElementById("food_category");
    const wineCategorySelect = document.getElementById("wine_category");
    const wineTypeSelect = document.getElementById("wine_type");

    if (foodCategorySelect) {
        foodCategorySelect.addEventListener("change", updateFoodItems);
    }

    if (wineCategorySelect) {
        wineCategorySelect.addEventListener("change", updateWineFields);
    }

    if (wineTypeSelect) {
        wineTypeSelect.addEventListener("change", updateWineFields);
    }

    updateFoodItems();
    updateWineFields();
});