# Contributing

Thanks for improving Awesome Human Motion.

## Add a Resource

1. Add the item to `data/resources.yml`.
2. Use one of the fixed categories:
   - Motion Capture
   - Motion Generation
   - Motion Interaction
   - Humanoid Simulation
   - Motion Video Generation
   - Datasets
   - Surveys and Benchmarks
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
featured Motion Capture entry.
