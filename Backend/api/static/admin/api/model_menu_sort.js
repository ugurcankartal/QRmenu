(function () {
  function getCsrfToken() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function collectModelNames(tbody) {
    return Array.prototype.map.call(
      tbody.querySelectorAll("tr[data-model-name]"),
      function (row) {
        return row.dataset.modelName;
      }
    );
  }

  function collectAppLabels(container) {
    return Array.prototype.map.call(
      container.querySelectorAll(".admin-app-module[data-app-label]"),
      function (module) {
        return module.dataset.appLabel;
      }
    );
  }

  function saveModelOrder(tbody) {
    return fetch(tbody.dataset.saveUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        app_label: tbody.dataset.appLabel,
        model_names: collectModelNames(tbody),
      }),
      credentials: "same-origin",
    });
  }

  function saveAppOrder(container) {
    return fetch(container.dataset.saveUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        app_labels: collectAppLabels(container),
      }),
      credentials: "same-origin",
    });
  }

  function initSortableTable(tbody) {
    var draggedRow = null;

    Array.prototype.forEach.call(
      tbody.querySelectorAll("tr[data-model-name]"),
      function (row) {
        var handle = row.querySelector(".admin-model-sort-handle");
        if (!handle) {
          return;
        }

        handle.addEventListener("mousedown", function () {
          row.draggable = true;
        });

        row.addEventListener("dragstart", function (event) {
          draggedRow = row;
          row.classList.add("is-dragging");
          event.dataTransfer.effectAllowed = "move";
          event.dataTransfer.setData("text/plain", row.dataset.modelName || "");
        });

        row.addEventListener("dragend", function () {
          row.draggable = false;
          row.classList.remove("is-dragging");
          draggedRow = null;
          saveModelOrder(tbody);
        });
      }
    );

    tbody.addEventListener("dragover", function (event) {
      event.preventDefault();
      if (!draggedRow) {
        return;
      }

      var target = event.target.closest("tr[data-model-name]");
      if (!target || target === draggedRow) {
        return;
      }

      var rect = target.getBoundingClientRect();
      var insertAfter = event.clientY > rect.top + rect.height / 2;
      if (insertAfter) {
        target.after(draggedRow);
      } else {
        target.before(draggedRow);
      }
    });
  }

  function initSortableApps(container) {
    var draggedModule = null;

    Array.prototype.forEach.call(
      container.querySelectorAll(".admin-app-module[data-app-label]"),
      function (module) {
        var handle = module.querySelector(".admin-app-sort-handle");
        if (!handle) {
          return;
        }

        handle.addEventListener("mousedown", function () {
          module.draggable = true;
        });

        module.addEventListener("dragstart", function (event) {
          draggedModule = module;
          module.classList.add("is-dragging-app");
          event.dataTransfer.effectAllowed = "move";
          event.dataTransfer.setData("text/plain", module.dataset.appLabel || "");
        });

        module.addEventListener("dragend", function () {
          module.draggable = false;
          module.classList.remove("is-dragging-app");
          draggedModule = null;
          saveAppOrder(container);
        });
      }
    );

    container.addEventListener("dragover", function (event) {
      event.preventDefault();
      if (!draggedModule) {
        return;
      }

      var target = event.target.closest(".admin-app-module[data-app-label]");
      if (!target || target === draggedModule) {
        return;
      }

      var rect = target.getBoundingClientRect();
      var insertAfter = event.clientY > rect.top + rect.height / 2;
      if (insertAfter) {
        target.after(draggedModule);
      } else {
        target.before(draggedModule);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".js-admin-model-sortable").forEach(initSortableTable);
    document.querySelectorAll(".js-admin-app-sortable").forEach(initSortableApps);
  });
})();
