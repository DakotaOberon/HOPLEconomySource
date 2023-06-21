import discord

from apps.source.discord.models import VoiceChannel, Member
from apps.source.activity.models import VoiceController, VoiceActivityTracker, VoiceActivityLongTermTracker
from apps.source.activity.settings import VOICE_CONFIG

from apps.source.bank.models import Account


def update_voice_activity_from_discord_member_voice_state(member: discord.Member, voice_state: discord.VoiceState):
    db_member = Member.objects.get(id=str(member.id))
    voice_activity_tracker, created = VoiceActivityTracker.objects.get_or_create(id=member.id, member=db_member)

    if created:
        voice_activity_tracker.rewards_left = VOICE_CONFIG['REWARDS_PER_DAY']

    if voice_state.channel is None:
        voice_activity_tracker.current_channel = None
        voice_activity_tracker.save()
        return

    voice_activity_tracker.current_channel = VoiceChannel.objects.filter(id=str(voice_state.channel.id)).first()
    voice_activity_tracker.video_on = voice_state.self_video
    voice_activity_tracker.streaming = voice_state.self_stream
    voice_activity_tracker.muted = voice_state.self_mute
    voice_activity_tracker.deafened = voice_state.self_deaf

    voice_activity_tracker.save()
    return

def get_activity_tracker_list():
    return list(VoiceActivityTracker.objects.filter(current_channel__isnull=False))

def get_global_multiplier(tracker: VoiceActivityTracker):
    if tracker.controller == None:
        tracker.controller = VoiceController.objects.first()
        tracker.save()

    multiplier_mapping = [
        (tracker.controller.is_holiday, VOICE_CONFIG['MULTIPLIERS']['HOLIDAY']),
        (tracker.controller.is_weekend, VOICE_CONFIG['MULTIPLIERS']['WEEKEND']),
    ]

    return sum(multiplier if condition else 0 for condition, multiplier in multiplier_mapping)  

def get_activity_tracker_multiplier(tracker: VoiceActivityTracker):
    multiplier = VOICE_CONFIG['MULTIPLIERS']['BASE']

    group_multiplier = VoiceActivityTracker.objects.filter(current_channel=tracker.current_channel).count() - 1
    group_multiplier = min(group_multiplier * VOICE_CONFIG['MULTIPLIERS']['GROUP'], VOICE_CONFIG['MULTIPLIERS']['GROUP_MAX'])
    global_multiplier = get_global_multiplier(tracker)

    multiplier_mapping = [
        (tracker.is_birthday,   VOICE_CONFIG['MULTIPLIERS']['BIRTHDAY']),
        (tracker.video_on,      VOICE_CONFIG['MULTIPLIERS']['VIDEO']),
        (tracker.streaming,     VOICE_CONFIG['MULTIPLIERS']['STREAMING']),
        (tracker.muted,         VOICE_CONFIG['MULTIPLIERS']['MUTE']),
        (tracker.deafened,      VOICE_CONFIG['MULTIPLIERS']['DEAF']),
    ]

    multiplier += sum(multiplier if condition else 0 for condition, multiplier in multiplier_mapping)
    multiplier += group_multiplier + global_multiplier

    return round(multiplier, VOICE_CONFIG['DECIMAL_PLACES'])

def get_minimum_multiplier(tracker: VoiceActivityTracker):
    return min(tracker.multipliers_data.keys())

def tick_member_activity_tracker(tracker: VoiceActivityTracker):
    tracker.ticks_till_reward -= 1
    tracker.ticks_spent_in_call += 1

    if tracker.ticks_till_reward > 0:
        tracker.save()
        return

    tracker.ticks_till_reward = VOICE_CONFIG['TICKS_PER_REWARD']

    multiplier = get_activity_tracker_multiplier(tracker)
    real_multiplier = multiplier

    if tracker.rewards_left <= 0:
        minimum_multiplier = round(float(get_minimum_multiplier(tracker)), VOICE_CONFIG['DECIMAL_PLACES'])

        if multiplier <= minimum_multiplier:
            tracker.save()
            return

        tracker.multipliers_data[str(minimum_multiplier)] -= 1

        if tracker.multipliers_data[str(minimum_multiplier)] <= 0:
            tracker.multipliers_data.pop(str(minimum_multiplier))

        real_multiplier = multiplier - minimum_multiplier
    else:
        tracker.rewards_left -= 1

    tracker.multipliers_data[str(multiplier)] = tracker.multipliers_data.get(str(multiplier), 0) + 1
    tracker.points_earned = round(tracker.points_earned + (VOICE_CONFIG['BASE_POINT_REWARD'] * real_multiplier), VOICE_CONFIG['DECIMAL_PLACES'])
    tracker.save()
    return

def updated_long_term_tracker_from_daily_tracker(long_term_tracker: VoiceActivityLongTermTracker, daily_tracker: VoiceActivityTracker):
    long_term_tracker.points_earned += daily_tracker.points_earned

    for multiplier, count in daily_tracker.multipliers_data.items():
        long_term_tracker.multipliers_data[multiplier] = long_term_tracker.multipliers_data.get(multiplier, 0) + count

    long_term_tracker.highest_multiplier = max(long_term_tracker.multipliers_data.keys())

    if daily_tracker.points_earned > long_term_tracker.highest_points_earned:
        long_term_tracker.highest_points_earned = daily_tracker.points_earned

    seconds_spent_in_call_today = daily_tracker.ticks_spent_in_call * VOICE_CONFIG['TICK_RATE']
    seconds_spent_video_on_today = daily_tracker.ticks_spent_video_on * VOICE_CONFIG['TICK_RATE']
    seconds_spent_streaming_today = daily_tracker.ticks_spent_streaming * VOICE_CONFIG['TICK_RATE']
    seconds_spent_deafened_today = daily_tracker.ticks_spent_deafened * VOICE_CONFIG['TICK_RATE']
    seconds_spent_muted_today = daily_tracker.ticks_spent_muted * VOICE_CONFIG['TICK_RATE']

    if seconds_spent_in_call_today > long_term_tracker.highest_time_spent_in_call:
        long_term_tracker.highest_time_spent_in_call = seconds_spent_in_call_today

    long_term_tracker.time_spent_in_call += seconds_spent_in_call_today
    long_term_tracker.time_spent_video_on += seconds_spent_video_on_today
    long_term_tracker.time_spent_streaming += seconds_spent_streaming_today
    long_term_tracker.time_spent_deafened += seconds_spent_deafened_today
    long_term_tracker.time_spent_muted += seconds_spent_muted_today

    long_term_tracker.save()

def daily_activity_tracker_reset(tracker: VoiceActivityTracker):
    long_term_tracker, created = VoiceActivityLongTermTracker.objects.get_or_create(id=tracker.member.id, member=tracker.member)
    updated_long_term_tracker_from_daily_tracker(long_term_tracker, tracker)

    citizen = tracker.member.citizen
    bank_account = Account.objects.get_or_create(owner=citizen)[0]
    bank_account.deposit(tracker.points_earned, VOICE_CONFIG['REWARD_CURRENCY_NAME'])

    tracker.daily_reset()

    tracker.rewards_left = VOICE_CONFIG['REWARDS_PER_DAY']
    tracker.save()
