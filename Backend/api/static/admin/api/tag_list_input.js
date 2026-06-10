(function () {
  function parseTags(rawValue) {
    if (!rawValue) {
      return [];
    }
    try {
      var parsed = JSON.parse(rawValue);
      if (!Array.isArray(parsed)) {
        return [];
      }
      return parsed
        .map(function (item) {
          return String(item).trim();
        })
        .filter(Boolean);
    } catch (error) {
      return [];
    }
  }

  function serializeTags(tags) {
    return JSON.stringify(tags);
  }

  function renderChips(widget, tags) {
    var chipsContainer = widget.querySelector(".tag-list-chips");
    chipsContainer.innerHTML = "";

    tags.forEach(function (tag, index) {
      var chip = document.createElement("span");
      chip.className = "tag-list-chip";
      chip.dataset.index = String(index);

      var label = document.createElement("span");
      label.className = "tag-list-chip-label";
      label.textContent = tag;

      var removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "tag-list-chip-remove";
      removeButton.setAttribute("aria-label", "Kaldır");
      removeButton.textContent = "×";

      chip.appendChild(label);
      chip.appendChild(removeButton);
      chipsContainer.appendChild(chip);
    });
  }

  function syncHiddenInput(widget, tags) {
    var hiddenInput = widget.querySelector('input[type="hidden"]');
    hiddenInput.value = serializeTags(tags);
  }

  function getTags(widget) {
    var hiddenInput = widget.querySelector('input[type="hidden"]');
    return parseTags(hiddenInput.value);
  }

  function commitEntry(widget) {
    var entry = widget.querySelector(".tag-list-entry");
    var value = entry.value.trim();
    if (!value) {
      return;
    }

    var tags = getTags(widget);
    if (tags.indexOf(value) === -1) {
      tags.push(value);
    }

    syncHiddenInput(widget, tags);
    renderChips(widget, tags);
    entry.value = "";
  }

  function removeTag(widget, index) {
    var tags = getTags(widget);
    tags.splice(index, 1);
    syncHiddenInput(widget, tags);
    renderChips(widget, tags);
  }

  function initTagListWidget(widget) {
    if (widget.dataset.tagListInitialized === "true") {
      return;
    }
    widget.dataset.tagListInitialized = "true";

    var tags = getTags(widget);
    renderChips(widget, tags);

    var entry = widget.querySelector(".tag-list-entry");

    entry.addEventListener("blur", function () {
      commitEntry(widget);
    });

    entry.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        commitEntry(widget);
      }
    });

    widget.addEventListener("click", function (event) {
      var removeButton = event.target.closest(".tag-list-chip-remove");
      if (!removeButton) {
        return;
      }
      event.preventDefault();
      var chip = removeButton.closest(".tag-list-chip");
      var index = Number(chip.dataset.index);
      removeTag(widget, index);
    });
  }

  function initAll(root) {
    root.querySelectorAll(".tag-list-widget").forEach(initTagListWidget);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initAll(document);
  });

  if (window.django && window.django.jQuery) {
    window.django.jQuery(document).on("formset:added", function (_event, row) {
      initAll(row.get(0));
    });
  }
})();
