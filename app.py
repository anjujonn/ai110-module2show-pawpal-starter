import streamlit as st
from pawpal_system import PetOwner, Pet, Task, Priority, Frequency

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────
def _parse_mins(time_str):
    """'HH:MM' → minutes since midnight, or None if unparseable."""
    if not time_str:
        return None
    try:
        h, m = time_str.strip().split(":")
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None

def _mins_to_str(mins):
    """Minutes since midnight → 'HH:MM'."""
    return f"{mins // 60:02d}:{mins % 60:02d}"

def _find_conflicts(task_pet_pairs):
    """Return a set of task ids whose time windows overlap with at least one other task."""
    timed = [
        (t, _parse_mins(t.specific_time))
        for t, _ in task_pet_pairs
        if _parse_mins(t.specific_time) is not None
    ]
    bad = set()
    for i, (ta, sa) in enumerate(timed):
        for j, (tb, sb) in enumerate(timed):
            if i >= j:
                continue
            if sa < sb + tb.duration and sb < sa + ta.duration:
                bad.add(id(ta))
                bad.add(id(tb))
    return bad

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state init ---
if "owners" not in st.session_state:
    st.session_state.owners = []
if "selected_owner_name" not in st.session_state:
    st.session_state.selected_owner_name = None
if "selected_pet_name" not in st.session_state:
    st.session_state.selected_pet_name = None

# ──────────────────────────────────────────
# OWNER PROFILE
# ──────────────────────────────────────────
st.subheader("Owner Profile")

with st.expander("Add New Owner", expanded=not bool(st.session_state.owners)):
    with st.form("owner_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            owner_name = st.text_input("Owner name", value="")
        with col2:
            owner_address = st.text_input("Address", value="")
        with col3:
            owner_phone = st.text_input("Phone number", value="")
        submitted_owner = st.form_submit_button("Add Owner")

    if submitted_owner:
        if not owner_name.strip():
            st.warning("Please enter an owner name.")
        elif any(o.name == owner_name.strip() for o in st.session_state.owners):
            st.warning(f"An owner named '{owner_name}' already exists.")
        else:
            new_owner = PetOwner.create_owner_profile(
                name=owner_name.strip(),
                address=owner_address,
                phone_number=owner_phone,
            )
            st.session_state.owners.append(new_owner)
            st.session_state.selected_owner_name = new_owner.name
            st.session_state.selected_pet_name = None
            st.success(f"Owner '{owner_name}' added.")
            st.rerun()

# ── Owner selector ──
if st.session_state.owners:
    owner_names = [o.name for o in st.session_state.owners]

    if st.session_state.selected_owner_name not in owner_names:
        st.session_state.selected_owner_name = owner_names[0]

    selected_owner_name = st.selectbox(
        "Select owner",
        owner_names,
        index=owner_names.index(st.session_state.selected_owner_name),
        key="owner_selector",
    )
    if selected_owner_name != st.session_state.selected_owner_name:
        st.session_state.selected_owner_name = selected_owner_name
        st.session_state.selected_pet_name = None
        st.rerun()

owner = next((o for o in st.session_state.owners if o.name == st.session_state.selected_owner_name), None)

# ──────────────────────────────────────────
# PETS
# ──────────────────────────────────────────
if owner:
    st.divider()
    st.subheader(f"Pets — {owner.name}")

    with st.expander("Add New Pet", expanded=not bool(owner.pets_list)):
        with st.form("pet_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                pet_name = st.text_input("Pet name", value="Mochi")
            with col2:
                species = st.selectbox("Species", ["dog", "cat", "other"])
            with col3:
                age = st.number_input("Age", min_value=0, max_value=30, value=2)
            with col4:
                gender = st.selectbox("Gender", ["Unknown", "Male", "Female"])
            col5, col6, col7 = st.columns(3)
            with col5:
                allergies = st.text_input("Allergies", value="")
            with col6:
                medical_bg = st.text_input("Medical background", value="")
            with col7:
                pet_notes = st.text_input("Notes", value="")
            add_pet_btn = st.form_submit_button("Add Pet")

        if add_pet_btn:
            existing_names = [p.name for p in owner.pets_list]
            if pet_name in existing_names:
                st.warning(f"A pet named '{pet_name}' already exists.")
            else:
                new_pet = Pet.create(
                    name=pet_name,
                    animal_type=species,
                    age=age,
                    gender=gender,
                    allergies=allergies,
                    medical_background=medical_bg,
                    notes=pet_notes,
                )
                owner.add_pet(new_pet)
                st.session_state.selected_pet_name = new_pet.name
                st.success(f"Pet '{pet_name}' added to {owner.name}'s profile.")
                st.rerun()

    # ── Pet selector ──
    if owner.pets_list:
        pet_names = [p.name for p in owner.pets_list]

        if st.session_state.selected_pet_name not in pet_names:
            st.session_state.selected_pet_name = pet_names[0]

        selected_name = st.selectbox(
            "Select pet to manage",
            pet_names,
            index=pet_names.index(st.session_state.selected_pet_name),
            key="pet_selector",
        )
        if selected_name != st.session_state.selected_pet_name:
            st.session_state.selected_pet_name = selected_name
            st.rerun()

        selected_pet = next(p for p in owner.pets_list if p.name == selected_name)

        # Pet profile info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Species:** {selected_pet.animal_type}")
        with col2:
            st.markdown(f"**Age:** {selected_pet.age} yr")
        with col3:
            st.markdown(f"**Gender:** {selected_pet.gender}")
        if selected_pet.allergies:
            st.markdown(f"**Allergies:** {selected_pet.allergies}")
        if selected_pet.medical_background:
            st.markdown(f"**Medical:** {selected_pet.medical_background}")
        if selected_pet.notes:
            st.caption(f"Notes: {selected_pet.notes}")

        if st.button(f"Remove {selected_pet.name} from profile", key="remove_pet_btn"):
            owner.remove_pet(selected_pet)
            st.session_state.selected_pet_name = owner.pets_list[0].name if owner.pets_list else None
            st.rerun()

        # ──────────────────────────────────────────
        # TASKS FOR SELECTED PET
        # ──────────────────────────────────────────
        st.divider()
        st.subheader(f"Tasks — {selected_pet.name}")

        with st.expander("Add New Task"):
            with st.form("task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    task_title = st.text_input("Task title", value="Morning walk")
                    task_type = st.text_input("Task type (e.g. Exercise, Feeding)", value="Exercise")
                    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
                with col2:
                    priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=2)
                    frequency = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"])
                    specific_time = st.text_input("Specific time (e.g. 08:00)", value="")
                task_notes = st.text_area("Notes", value="", height=68)
                add_task_btn = st.form_submit_button("Add Task")

            if add_task_btn:
                task = Task.create_task(
                    name=task_title,
                    type_of_task=task_type,
                    duration=int(duration),
                    priority=Priority(priority),
                    frequency=Frequency(frequency),
                    specific_time=specific_time.strip() if specific_time.strip() else None,
                    notes=task_notes,
                )
                selected_pet.add_task(task)
                st.success(f"Task '{task_title}' added to {selected_pet.name}.")
                st.rerun()

        # Task list with tabs
        if selected_pet.tasks_list:
            tab_all, tab_pending, tab_done = st.tabs(
                [f"All ({len(selected_pet.tasks_list)})",
                 f"Pending ({len(selected_pet.get_pending_tasks())})",
                 f"Completed ({len(selected_pet.get_completed_tasks())})"]
            )

            def render_task_rows(tasks, pet, tab_key):
                """Render a list of task rows with Done and Delete buttons.

                tasks   : list of Task objects to display
                pet     : the Pet that owns these tasks (passed to mark_complete/delete)
                tab_key : unique string prefix for Streamlit widget keys to avoid collisions
                          across the All / Pending / Completed tabs
                """
                if not tasks:
                    st.info("No tasks in this view.")
                    return
                for task in tasks:
                    icon = "✅" if task.completed else "⏳"
                    time_label = f" @ {task.specific_time}" if task.specific_time else ""
                    col1, col2, col3 = st.columns([5, 1, 1])
                    with col1:
                        st.markdown(
                            f"{icon} **{task.name}**{time_label} &nbsp;|&nbsp; "
                            f"{task.duration} min &nbsp;|&nbsp; "
                            f"`{task.priority.value.upper()}` &nbsp;|&nbsp; "
                            f"{task.frequency.value} &nbsp;|&nbsp; "
                            f"*{task.type_of_task}*"
                        )
                        if task.notes:
                            st.caption(task.notes)
                    with col2:
                        if not task.completed:
                            if st.button("Done", key=f"{tab_key}_done_{id(task)}"):
                                task.mark_complete(pet=pet)
                                st.rerun()
                    with col3:
                        if st.button("Delete", key=f"{tab_key}_del_{id(task)}"):
                            task.delete_task(pet)
                            st.rerun()

            with tab_all:
                render_task_rows(selected_pet.tasks_list, selected_pet, "all")
            with tab_pending:
                render_task_rows(selected_pet.get_pending_tasks(), selected_pet, "pend")
            with tab_done:
                render_task_rows(selected_pet.get_completed_tasks(), selected_pet, "done")
        else:
            st.info("No tasks yet. Add one above.")

# ──────────────────────────────────────────
# MASTER SCHEDULE  (all owners · all pets)
# ──────────────────────────────────────────
st.divider()
st.subheader("Master Schedule")

# Collect (task, pet, owner) across every owner
all_task_pet_owner = [
    (task, pet, o)
    for o in st.session_state.owners
    for pet in o.pets_list
    for task in pet.tasks_list
]

if not all_task_pet_owner:
    st.info("Add owners, pets, and tasks to build the master schedule.")
else:
    # ── Filters ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        owner_opts = ["All owners"] + [o.name for o in st.session_state.owners]
        ms_owner = st.selectbox("Filter by owner", owner_opts, key="ms_owner")
    with col2:
        # Pet list changes based on owner filter
        if ms_owner == "All owners":
            pet_name_opts = sorted({pet.name for _, pet, _ in all_task_pet_owner})
        else:
            pet_name_opts = sorted({
                pet.name for _, pet, o in all_task_pet_owner if o.name == ms_owner
            })
        ms_pet = st.selectbox("Filter by pet", ["All pets"] + pet_name_opts, key="ms_pet")
    with col3:
        ms_status = st.selectbox(
            "Filter by status", ["All", "Pending", "Completed"], key="ms_status"
        )
    with col4:
        ms_priority = st.selectbox(
            "Filter by priority",
            ["All", "urgent", "high", "medium", "low"],
            key="ms_priority",
        )

    filtered = all_task_pet_owner
    if ms_owner != "All owners":
        filtered = [(t, p, o) for t, p, o in filtered if o.name == ms_owner]
    if ms_pet != "All pets":
        filtered = [(t, p, o) for t, p, o in filtered if p.name == ms_pet]
    if ms_status == "Pending":
        filtered = [(t, p, o) for t, p, o in filtered if not t.completed]
    elif ms_status == "Completed":
        filtered = [(t, p, o) for t, p, o in filtered if t.completed]
    if ms_priority != "All":
        filtered = [(t, p, o) for t, p, o in filtered if t.priority.value == ms_priority]

    def _sort_key(tpo):
        """Return a (bucket, minutes) tuple so timed tasks sort before untimed ones.

        tpo : (task, pet, owner) triple from the master schedule list
        Timed tasks get bucket 0 and are sorted by their start minute.
        Untimed tasks get bucket 1 and all share the same secondary key (0),
        keeping them in their original relative order at the bottom.
        """
        mins = _parse_mins(tpo[0].specific_time)
        return (0, mins) if mins is not None else (1, 0)

    sorted_triples = sorted(filtered, key=_sort_key)

    # Conflict detection runs on ALL timed tasks across all owners/pets
    conflict_ids = _find_conflicts(
        [(t, p) for t, p, _ in all_task_pet_owner if t.specific_time]
    )

    # ── Metrics ──
    total_dur = sum(t.duration for t, _, _ in sorted_triples)
    pending_n = sum(1 for t, _, _ in sorted_triples if not t.completed)
    conflict_n = sum(1 for t, _, _ in filtered if id(t) in conflict_ids)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tasks shown", len(sorted_triples))
    with col2:
        st.metric("Pending", pending_n)
    with col3:
        st.metric("Est. duration", f"{total_dur} min")
    with col4:
        st.metric("Time conflicts", conflict_n)

    if conflict_n:
        st.warning(
            f"{conflict_n} task(s) have overlapping time windows. "
            "Tasks marked ⚠️ below need attention."
        )

    # ── Recurring task reset ──
    completed_recurring = [
        (t, p, o) for t, p, o in all_task_pet_owner
        if t.frequency.value != "once" and t.completed
    ]
    if completed_recurring:
        with st.expander("Reset Recurring Tasks"):
            st.caption("Mark completed recurring tasks as pending again to start a new cycle.")
            rcol1, rcol2, rcol3 = st.columns(3)
            for freq_val, col in [("daily", rcol1), ("weekly", rcol2), ("monthly", rcol3)]:
                group = [(t, p, o) for t, p, o in completed_recurring if t.frequency.value == freq_val]
                if group:
                    with col:
                        if st.button(f"Reset {len(group)} {freq_val}", key=f"reset_{freq_val}"):
                            for t, _, __ in group:
                                t.completed = False
                            st.rerun()

    # ── Task rows ──
    def _render_master_row(task, pet, o, key_prefix):
        """Render a single task row in the master schedule.

        task       : Task object to display
        pet        : Pet that owns this task
        o          : PetOwner that owns the pet
        key_prefix : short string ('ms_t' or 'ms_u') prepended to Streamlit widget
                     keys so timed and untimed rows never share a key
        Highlights conflicting tasks with a warning badge and shows the computed
        end time for tasks that have a specific_time set.
        """
        is_conflict = id(task) in conflict_ids
        icon = "✅" if task.completed else "⏳"
        freq_tag = f" `{task.frequency.value}`" if task.frequency.value != "once" else ""
        conflict_tag = " ⚠️" if is_conflict else ""

        if task.specific_time:
            start_m = _parse_mins(task.specific_time)
            time_range = f"{task.specific_time}–{_mins_to_str(start_m + task.duration)}"
        else:
            time_range = f"Anytime · {task.duration} min"

        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(
                f"{icon}{conflict_tag} **{task.name}** &nbsp;|&nbsp; "
                f"👤 {o.name} · 🐾 {pet.name} &nbsp;|&nbsp; "
                f"{time_range} &nbsp;|&nbsp; "
                f"`{task.priority.value.upper()}`{freq_tag}"
            )
            if task.notes:
                st.caption(task.notes)
        with col2:
            if not task.completed:
                if st.button("Done", key=f"{key_prefix}_done_{id(task)}"):
                    task.mark_complete(pet=pet)
                    st.rerun()

    if not sorted_triples:
        st.info("No tasks match your filters.")
    else:
        timed_triples   = [(t, p, o) for t, p, o in sorted_triples if t.specific_time]
        untimed_triples = [(t, p, o) for t, p, o in sorted_triples if not t.specific_time]

        if timed_triples:
            st.markdown("**Scheduled**")
            for task, pet, o in timed_triples:
                _render_master_row(task, pet, o, "ms_t")

        if untimed_triples:
            st.markdown("**Anytime**")
            for task, pet, o in untimed_triples:
                _render_master_row(task, pet, o, "ms_u")

# ── Per-owner summary ──
if owner and owner.pets_list:
    st.divider()
    st.subheader(f"Summary — {owner.name}")
    all_tasks   = owner.get_all_tasks()
    all_pending = owner.get_all_pending_tasks()
    urgent_all  = [t for t in all_tasks if t.priority == Priority.URGENT]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total tasks (all pets)", len(all_tasks))
    with col2:
        st.metric("Pending (all pets)", len(all_pending))
    with col3:
        st.metric("Urgent (all pets)", len(urgent_all))

# ── All-owners summary ──
if len(st.session_state.owners) > 1:
    st.divider()
    st.subheader("All Owners Summary")
    for o in st.session_state.owners:
        tasks   = o.get_all_tasks()
        pending = o.get_all_pending_tasks()
        urgent  = [t for t in tasks if t.priority == Priority.URGENT]
        pets_label = ", ".join(p.name for p in o.pets_list) if o.pets_list else "no pets"
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.markdown(f"**{o.name}** — {pets_label}")
        with col2:
            st.metric("Tasks", len(tasks), label_visibility="collapsed")
        with col3:
            st.metric("Pending", len(pending), label_visibility="collapsed")
        with col4:
            st.metric("Urgent", len(urgent), label_visibility="collapsed")
