// Drag-and-drop reordering for the admin project list.
// On drop, POSTs the full ordered id list to the reorder API as JSON.
(function () {
  const list = document.getElementById("project-list");
  if (!list) return;

  const reorderUrl = list.dataset.reorderUrl;
  let draggedRow = null;

  list.addEventListener("dragstart", (event) => {
    const row = event.target.closest(".admin-row[draggable='true']");
    if (!row) return;
    draggedRow = row;
    row.classList.add("dragging");
    event.dataTransfer.effectAllowed = "move";
  });

  list.addEventListener("dragend", () => {
    if (draggedRow) draggedRow.classList.remove("dragging");
    draggedRow = null;
    persistOrder();
  });

  list.addEventListener("dragover", (event) => {
    event.preventDefault();
    const afterElement = getRowAfter(list, event.clientY);
    if (!draggedRow) return;
    if (afterElement == null) {
      list.appendChild(draggedRow);
    } else {
      list.insertBefore(draggedRow, afterElement);
    }
  });

  function getRowAfter(container, y) {
    const rows = [...container.querySelectorAll(".admin-row[draggable='true']:not(.dragging)")];
    return rows.reduce(
      (closest, row) => {
        const box = row.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
          return { offset, element: row };
        }
        return closest;
      },
      { offset: Number.NEGATIVE_INFINITY, element: null }
    ).element;
  }

  function persistOrder() {
    const ids = [...list.querySelectorAll(".admin-row[draggable='true']")].map((row) =>
      parseInt(row.dataset.id, 10)
    );
    fetch(reorderUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order: ids }),
    }).catch(() => {
      // Best-effort; a page refresh will show the last saved order if this fails.
    });
  }
})();
