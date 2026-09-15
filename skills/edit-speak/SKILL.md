---
name: edit-speak
description: Modify voice, tone, frequency, or task triggers in your existing speak configuration.
disable-model-invocation: true
---

Update an existing agent speech configuration without re-running engine setup.

## Step 1: Locate and Read Active Configuration

Check for existing configuration in this order:

1. `./.speak.md` in the current repository root.
2. `~/.config/speak/config.md` in the user home directory.

If neither file exists, inform the user:
`No speak configuration found. Run /setup-speak first to install a TTS engine and create an initial configuration.`

Otherwise, read the YAML frontmatter and display the current settings:

```
Active Voice:      <voice> (<engine>)
Tone:              <tone>
Frequency:         <frequency>
Volume Multiplier: <volume>
```

## Step 2: Prompt for Changes

Ask the user what they would like to adjust:

1. **Change Voice**: Present available voices for the currently active engine. Offer to play a short preview if requested.
2. **Change Tone**: Switch between `conversational`, `formal`, or `minimal`.
3. **Change Frequency**: Switch between `completions-and-errors`, `all-milestones`, `errors-only`, or `silent`.
4. **Volume Adjustment**: Adjust audio gain (e.g. 1.0 for default, 1.5 for moderate boost, 2.5 for noisy environments).
5. **Toggle Task Triggers**: Enable or disable speech for specific categories (builds, tests, reviews, research).
6. **Mute / Unmute**: Temporarily set frequency to `silent` or restore previous frequency.

## Step 3: Write Updates and Confirm

Update the YAML frontmatter in the active configuration file. Keep existing comments and structure intact.

Confirm the changes with a short 1-sentence audible test using the updated settings, then report the updated configuration summary in text.
