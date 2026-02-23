import streamlit as st
from StoryHelper import StoryHelper
from PIL import Image

# ─── Page Configuration ───────────────────────────────────────────────────────
# Must be the first Streamlit call in the script.
st.set_page_config(
    page_title="StoryMaker - Run wild with your ideas!",
    page_icon="📖",
    layout="wide"
)

# ─── StoryHelper Instance ─────────────────────────────────────────────────────
# @st.cache_resource creates ONE shared instance for the entire session.
# The same StoryHelper (and its underlying HTTP client) is reused on every
# Streamlit rerun rather than creating a new object each time.
@st.cache_resource
def get_story_helper():
    return StoryHelper()

helper = get_story_helper()


# ─── Data Loading via StoryHelper ─────────────────────────────────────────────
# @st.cache_data stores the return values so the JSON files are only read once
# per session, even though Streamlit reruns the script on every interaction.

@st.cache_data
def load_all_prompts():
    """Return the full list of system prompt dicts via StoryHelper."""
    return helper.get_all_system_prompts()


@st.cache_data
def load_all_stories():
    """Return all 10 story type dicts via StoryHelper.

    get_all_helpers() requires explicit 0-based indices, so we pass the full
    range of 10 stories (indices 0–9).
    """
    return helper.get_all_helpers(list(range(10)))


system_prompts = load_all_prompts()
story_types    = load_all_stories()

# Build a quick-lookup dict so fetching a story by its id is O(1).
# story is a StoryRecord (namedtuple), so story.id uses attribute access.
# e.g.  story_lookup[3]  →  the StoryRecord for "The Tortured Genius"
story_lookup = {story.id: story for story in story_types}


# ─── Page Header ──────────────────────────────────────────────────────────────
st.title("📖 StoryMaker - Run wild with your ideas!")
st.markdown(
    "Browse the available system prompts and the story types each one supports. "
    "Click any prompt card to expand it and see its linked stories."
)
st.divider()


# ─── Session State ────────────────────────────────────────────────────────────
# generated_stories maps StoryRecord → generated text.
# StoryRecord is a namedtuple (immutable + hashable), so it can be used as a
# dictionary key — this is the hashability use case.
if "generated_stories" not in st.session_state:
    st.session_state.generated_stories = {}


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Browse", "📚 Created Stories"])

with tab1:

    # ─── System Prompt Cards ──────────────────────────────────────────────────
    # One collapsible expander per entry in story_system_prompts.json.
    for prompt in system_prompts:

        pid            = prompt["prompt_id"]
        expander_label = f"**{prompt['label']}**  ·  Prompt #{pid}"

        with st.expander(expander_label, expanded=False):

            # ── Prompt metadata ───────────────────────────────────────────────

            st.markdown("##### Best For")
            st.info(prompt["best_for"])

            # Read-only text area keeps the full prompt readable without blowing
            # up the page height. disabled=True prevents editing.
            st.markdown("##### System Prompt")
            st.text_area(
                label="system_prompt",
                value=prompt["system_prompt"],
                height=160,
                disabled=True,
                label_visibility="collapsed"
            )

            st.markdown("---")

            # ── Story sub-boxes ───────────────────────────────────────────────
            # One bordered container per story_id linked to this system prompt.
            story_count = len(prompt["story_ids"])
            st.markdown(f"##### Stories  `{story_count} linked`")

            for story_id in prompt["story_ids"]:

                story = story_lookup.get(story_id)
                if story is None:
                    st.warning(f"Story ID {story_id} not found in story_types.json.")
                    continue

                # ── Session state keys ────────────────────────────────────────
                # Each prompt + story combination gets its own pair of keys so that
                # generating one story doesn't affect the state of any other card.
                #
                # key_show   → bool: whether the generated story panel is visible
                # key_result → str:  the generated story text, persists across reruns
                key_show   = f"show_{pid}_{story_id}"
                key_result = f"result_{pid}_{story_id}"

                # Initialise session state on first render
                if key_show not in st.session_state:
                    st.session_state[key_show] = False
                if key_result not in st.session_state:
                    st.session_state[key_result] = ""

                # border=True draws a visible card outline — requires Streamlit ≥ 1.29
                with st.container(border=True):

                    img_col, info_col = st.columns([1, 2], gap="large")

                    # ── Left column: poster image ──────────────────────────────
                    with img_col:
                        # get_helper_image() returns a PIL Image on success or an
                        # error string if the file is missing / unreadable.
                        img_result = helper.get_helper_image(story_id, story.protagonist)

                        if isinstance(img_result, Image.Image):
                            st.image(img_result, use_container_width=True)
                        else:
                            st.markdown(f"*Image unavailable — {img_result}*")

                    # ── Right column: story details + generate button ───────────
                    # generate_clicked is declared here so it is always defined
                    # when we reach the full-width section below the columns.
                    generate_clicked = False

                    with info_col:
                        st.markdown(f"### {story.protagonist}")
                        st.markdown(f"*{story.description}*")
                        st.markdown("---")

                        fields = [
                            ("Setting",       story.setting),
                            ("Plot",          story.plot),
                            ("Conflict",      story.conflict),
                            ("Theme",         story.theme),
                            ("Point of View", story.point_of_view),
                        ]

                        for field_label, field_value in fields:
                            st.markdown(f"**{field_label}:** {field_value}")

                        st.markdown("---")

                        # Show the generate button only when no story is displayed.
                        # Once a story is generated, this button is hidden and the
                        # Close button (below) takes its place.
                        if not st.session_state[key_show]:
                            generate_clicked = st.button(
                                "✍️ Generate Story",
                                key=f"gen_{pid}_{story_id}",
                                use_container_width=True
                            )

                    # ── Full-width panel below both columns ────────────────────
                    # Rendered inside the container but outside the columns so it
                    # spans the full card width — giving the story text more room.

                    if generate_clicked:
                        # st.write_stream() consumes the generate_story() generator,
                        # renders each chunk to the page as it arrives, and returns
                        # the complete assembled text when the stream finishes.
                        st.divider()
                        result = st.write_stream(
                            helper.generate_story(
                                prompt["system_prompt"],
                                story.protagonist,
                                story.description,
                                story.setting,
                                story.plot,
                                story.conflict,
                                story.theme,
                                story.point_of_view
                            )
                        )
                        # Persist the result so it survives the next rerun, then
                        # rerun to replace the live stream with a stable text area.
                        st.session_state[key_result] = result
                        st.session_state[key_show]   = True
                        # Store in generated_stories using StoryRecord as the key.
                        # This works because StoryRecord is hashable (namedtuple).
                        st.session_state.generated_stories[story] = result
                        st.rerun()

                    elif st.session_state[key_show]:
                        # A story was previously generated — show it in a read-only
                        # text area that persists across reruns via session state.
                        st.divider()
                        st.markdown("**Generated Story**")
                        st.text_area(
                            label="story_output",
                            value=st.session_state[key_result],
                            height=400,
                            disabled=True,
                            label_visibility="collapsed"
                        )

                        # Close button: clears the result panel and closes the
                        # StoryMaker HTTP client via StoryHelper.close_instance().
                        if st.button(
                            "Close",
                            key=f"close_{pid}_{story_id}",
                            use_container_width=True
                        ):
                            helper.close_instance()
                            st.session_state[key_show]   = False
                            st.session_state[key_result] = ""
                            st.rerun()


with tab2:

    # ─── Created Stories ──────────────────────────────────────────────────────
    # Iterates over generated_stories, which is keyed by StoryRecord instances.
    # Because StoryRecord is a namedtuple it is hashable and can serve as a
    # dict key — each entry maps a story archetype to its generated text.
    st.markdown("### Stories generated this session")

    if not st.session_state.generated_stories:
        st.info("No stories generated yet. Head to **Browse** and hit ✍️ **Generate Story**!")
    else:
        for record, text in st.session_state.generated_stories.items():
            with st.expander(f"**{record.protagonist}** — {record.setting}", expanded=False):
                st.markdown(f"*{record.description}*")
                st.markdown("---")
                st.text_area(
                    label="story_output",
                    value=text,
                    height=400,
                    disabled=True,
                    label_visibility="collapsed"
                )
