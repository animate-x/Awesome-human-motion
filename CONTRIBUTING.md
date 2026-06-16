# Contributing

Thanks for improving Awesome Human Motion.

## Add a Resource

1. Add the item to `data/resources.yml`.
2. Use one of the fixed categories:
   - Reviews and Surveys
   - Motion Capture
   - Human Pose Estimation and Motion Reconstruction
   - Motion Generation
   - Motion Editing
   - Motion Stylization
   - Motion Interaction
   - Human-Object and Human-Scene Interaction
   - Humanoid Simulation and Robot Motion
   - Motion Video Generation
   - Human Avatar and Reconstruction
   - Human Motion Understanding
   - Datasets and Benchmarks
   - Bio Motion and Biomechanics
3. Use `YYYY-MM` for `date`.
4. Use `OWNER/REPO` for `github`; leave optional links empty when unavailable.
5. Run:

```bash
python scripts/build_readme.py
python scripts/build_readme.py --check
python scripts/validate_resources.py
```

## Sorting

Items are generated newest first within each category. AIMoCap is pinned as the
first Motion Capture entry.
