# Test Project Updates Required

## CoinFrame Tests
- [ ] Update `test_coin_frame_initialization` to include new GPU device and view mode attributes
- [ ] Add new test `test_coin_frame_gpu_operations` to verify GPU/CPU device selection
- [ ] Add new test `test_coin_view_modes` to verify all ViewMode enum options
- [ ] Add new test `test_progressive_display` for large result sets
- [ ] Add new test `test_statistical_summary` for statistics view mode
- [ ] Update `test_handle_flip_coins` to include metadata tracking and GPU processing

## StandardDiceFrame Tests
- [ ] Update `test_standard_dice_frame_initialization` to include GPU device attribute
- [ ] Add new test `test_dice_gpu_operations` for GPU-accelerated rolls
- [ ] Add new test `test_dice_view_modes` for different display modes
- [ ] Add new test `test_batch_processing` for large dice rolls
- [ ] Update `test_validate_dice_input` to include scientific notation
- [ ] Add new test `test_progressive_display_dice` for large result sets

## CustomDiceFrame Tests
- [ ] Update `test_custom_dice_frame_initialization` to include GPU device
- [ ] Add new test `test_custom_dice_gpu_operations`
- [ ] Add new test `test_virtual_display_mode`
- [ ] Add new test `test_batch_processing_custom_dice`
- [ ] Update `test_roll_custom_dice` to include GPU acceleration
- [ ] Add new test `test_statistical_display_custom`

## Game History Tests
- [ ] Update `test_track_game_history` to include GPU metadata
- [ ] Add new test `test_game_history_persistence`
- [ ] Add new test `test_history_statistics`

## Performance Tests
- [ ] Add new test `test_gpu_vs_cpu_performance`
- [ ] Add new test `test_memory_usage_large_rolls`
- [ ] Add new test `test_display_performance`

## Error Handling Tests
- [ ] Add new test `test_gpu_fallback`
- [ ] Add new test `test_memory_overflow_handling`
- [ ] Add new test `test_invalid_view_mode_handling`

## Integration Tests
- [ ] Add new test `test_cross_frame_history`
- [ ] Add new test `test_multi_frame_gpu_usage`
- [ ] Add new test `test_combined_statistics`
