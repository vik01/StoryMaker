import streamlit as st
from StoryHelper import StoryHelper
from PIL import Image

# ─── Page Configuration ───────────────────────────────────────────────────────
# Must be the first Streamlit call in the script.
st.set_page_config(
    page_title="Story Reference Guide",
    page_icon="📖",
    layout="wide"
)

# ─── StoryHelper Instance ─────────────────────────────────────────────────────
# @st.cache_resource creates ONE shared instance for the entire session.
# This is intentional — when we add a generate button later, the same
# StoryHelper object (and its underlying StoryMaker HTTP client) will be
# reused rather than creating a new connection on every Streamlit rerun.
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
    """Return the full list of story type dicts via StoryHelper."""
    return helper.get_all_helpers()


system_prompts = load_all_prompts()
story_types    = load_all_stories()

# Build a quick-lookup dict so fetching a story by id is O(1).
# e.g.  story_lookup[3]  →  the full dict for "The Tortured Genius"
story_lookup = {story["id"]: story for story in story_types}


# ─── Page Header ──────────────────────────────────────────────────────────────
st.title("📖 Story Reference Guide")
st.markdown(
    "Browse the available system prompts and the story types each one supports. "
    "Click any prompt card to expand it and see its linked stories."
)
st.divider()


# ─── System Prompt Cards ──────────────────────────────────────────────────────
# One collapsible expander per entry in story_system_prompts.json.
for prompt in system_prompts:

    expander_label = f"**{prompt['label']}**  ·  Prompt #{prompt['prompt_id']}"

    with st.expander(expander_label, expanded=False):

        # ── Prompt metadata ───────────────────────────────────────────────────

        st.markdown("##### Best For")
        st.info(prompt["best_for"])

        # Read-only text area keeps the full prompt readable without blowing
        # up the page. disabled=True prevents editing.
        st.markdown("##### System Prompt")
        st.text_area(
            label="system_prompt",
            value=prompt["system_prompt"],
            height=160,
            disabled=True,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # ── Story sub-boxes ───────────────────────────────────────────────────
        # One bordered container per story_id linked to this system prompt.
        story_count = len(prompt["story_ids"])
        st.markdown(f"##### Stories  `{story_count} linked`")

        for story_id in prompt["story_ids"]:

            story = story_lookup.get(story_id)
            if story is None:
                st.warning(f"Story ID {story_id} not found in story_types.json.")
                continue

            # border=True draws a visible card outline — requires Streamlit ≥ 1.29
            with st.container(border=True):

                img_col, info_col = st.columns([1, 2], gap="large")

                # ── Left column: poster image ──────────────────────────────
                with img_col:
                    # get_helper_image() takes the int story_id (pads it internally)
                    # and the protagonist name.  It returns a PIL Image on success
                    # or an error string ("File not found." / "Cannot open the image.")
                    # if the file is missing or unreadable.
                    protagonist = story["characters"]["protagonist"]
                    img_result  = helper.get_helper_image(story_id, protagonist)

                    if isinstance(img_result, Image.Image):
                        st.image(img_result, use_container_width=True)
                    else:
                        # Surface the exact error from StoryHelper so it's easy to debug
                        st.markdown(f"*Image unavailable — {img_result}*")

                # ── Right column: story details (everything except id) ──────
                with info_col:
                    description = story["characters"]["description"]

                    st.markdown(f"### {protagonist}")
                    st.markdown(f"*{description}*")
                    st.markdown("---")

                    # Iterate over fields in display order
                    fields = [
                        ("Setting",       story["setting"]),
                        ("Plot",          story["plot"]),
                        ("Conflict",      story["conflict"]),
                        ("Theme",         story["theme"]),
                        ("Point of View", story["point_of_view"]),
                    ]

                    for field_label, field_value in fields:
                        st.markdown(f"**{field_label}:** {field_value}")

                    # ── Generate button placeholder ────────────────────────
                    # This is where the generate button will go once you are
                    # ready to wire it up. When clicked it will pass the story
                    # data and the parent system prompt to StoryHelper, which
                    # will call StoryMaker.generate() to build out the story.
                    #
                    # Example (not yet active):
                    # if st.button("Generate Story", key=f"gen_{prompt['prompt_id']}_{story_id}"):
                    #     with st.spinner("Generating..."):
                    #         result = helper.generate(prompt=story["plot"])
                    #     st.markdown(result)
